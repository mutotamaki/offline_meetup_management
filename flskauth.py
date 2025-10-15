from flask import Flask, request, render_template, session, redirect, url_for
import psycopg2
import hashlib
from datetime import timedelta
#データベースの設定は各自のものに修正すること
connection = psycopg2.connect("host=localhost dbname=mutotamaki user=mutotamaki password=rl2C1CdD")

app = Flask(__name__)
#この鍵はなんでも良く、乱数で生成する。このままでもいい
app.config['SECRET_KEY'] = b'PfnlrpCBaLCFKt39'
#セッションは30日残る設定
app.permanent_session_lifetime = timedelta(days=30)

#強制的にhttpsへリダイレクト
@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url)

#ここが最重要、認証後のページのサンプル
@app.route("/", methods=['GET', 'POST'])
def mypage():
    if "uid" in session and session["uid"]>0 and \
      "uname" in session and len(session["uname"])>0:
        uid=session["uid"]
        uname=session["uname"]
        return render_template("index.html",title="my page",uid=uid,uname=uname)
    else:
        return redirect("./login")
#ここまで
#このほかに認証後のページを作りたい場合上をベースに中身を作成すること。
#ユーザ名、ユーザIDは引き出してあるので、このあたりを利用して各自のサービスを構築してください。

@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html", title="login form")

@app.route('/regist', methods=['GET'])
def regist():
    return render_template("regist.html", title="regist form")

@app.route('/logingin', methods=['POST'])
def logingin():
    if request.method == 'POST' \
        and "emf" in request.form and "pwf" in request.form \
        and len(request.form['emf'])>0 and len(request.form['pwf'])>0:
        emf=request.form['emf']
        pwf=request.form['pwf']
        cur = connection.cursor()
        cur.execute("select count(uid) from flskauth where email='%s';" % (emf))
        res = cur.fetchone()
        cur.close()
        if res[0]>0:
            cur = connection.cursor()
            cur.execute("select uid,pw,uname from flskauth where email='%s';" % (emf))
            res = cur.fetchone()
            cur.close()
            cpw=hashlib.sha512(pwf.encode("utf-8")).hexdigest()
            if cpw==res[1]:
                session["uid"]=res[0]
                session["uname"]=res[2]
                return redirect("./")
            else:
                return redirect("./login")
        else:
            return redirect("./login")
    else:
        return redirect("./login")


@app.route('/registing', methods=['POST'])
def registing():
    msg=list()
    aflag=0;
    if request.method == 'POST' \
        and "unf" in request.form and "emf" in request.form \
        and "unf" in request.form and "emf" in request.form \
        and "pwf1" in request.form and "pwf2" in request.form \
        and len(request.form['unf'])>0 and len(request.form['emf'])>0 \
        and len(request.form['unf'])>0 and len(request.form['emf'])>0 \
        and len(request.form['pwf1'])>0 and len(request.form['pwf2'])>0:
        unf=request.form['unf']
        emf=request.form['emf']
        pwf1=request.form['pwf1']
        pwf2=request.form['pwf2']
        cur = connection.cursor()
        cur.execute("select count(uid) from flskauth where email='%s';" % (emf))
        res = cur.fetchone()
        cur.close()
        if res[0]>0:
            msg=msg+["このアドレスは既に登録されています。"]
        elif pwf1 != pwf2:
            msg=msg+["パスワードが一致しませんでした。"]
            aflag=2;  # regist.htmlに戻るフラグ
        else:
            cur = connection.cursor()
            epw=hashlib.sha512(pwf1.encode("utf-8")).hexdigest()
            cur.execute("insert into flskauth(uname,email,pw) \
                values('%s','%s','%s');" % (unf, emf,epw))
            connection.commit()
            cur.close()
            msg=msg+["登録完了しました。"]
            aflag=1;
    else:
        msg=msg+["フォームはすべて必須項目です。"]

    return render_template("registing.html", title="registing an user", message=msg, aflag=aflag)

@app.route('/logout')
def logout():
    session.pop("uid", None)
    session.pop("uname", None)
    return redirect("./")

@app.route('/host', methods=['GET', 'POST'])
def host():
    if "uid" in session and session["uid"]>0 and \
      "uname" in session and len(session["uname"])>0:
        uid=session["uid"]
        uname=session["uname"]
        return render_template("host.html",title="host page",uid=uid,uname=uname)
    

@app.route('/event_setting_confirm', methods=['POST'])
def event_setting_confirm():
    if "uid" not in session:
        return redirect("./login")
    
    # フォームデータを取得
    event_data = {
        'event_name': request.form.get('event_name'),
        'event_date': request.form.get('event_date'),
        'event_time_start': request.form.get('event_time_start'),
        'event_time_end': request.form.get('event_time_end'),
        'event_place': request.form.get('event_place'),
        'event_fee': request.form.get('event_fee'),
        'event_member': request.form.get('event_member'),
        'event_cancel': request.form.get('event_cancel'),
        'event_cancel_case': request.form.get('event_cancel_case'),
        'event_deadline': request.form.get('event_deadline'),
        'event_detail': request.form.get('event_detail')
    }
    
    return render_template("event_setting_confirm.html", **event_data)

@app.route('/event_list', methods=['GET', 'POST'])
def event_list():
    if "uid" not in session:
        return redirect("./login")
    
    # POSTの場合はイベント登録処理
    if request.method == 'POST':
        # イベントデータをデータベースに登録
        cur = connection.cursor()
        cur.execute("""
            INSERT INTO events (host_uid, event_name, event_date, event_time_start, 
                               event_time_end, event_place, event_fee, event_member, 
                               event_cancel, event_cancel_case, event_deadline, event_detail)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session["uid"],
            request.form.get('event_name'),
            request.form.get('event_date'),
            request.form.get('event_time_start'),
            request.form.get('event_time_end'),
            request.form.get('event_place'),
            request.form.get('event_fee'),
            request.form.get('event_member'),
            request.form.get('event_cancel'),
            request.form.get('event_cancel_case'),
            request.form.get('event_deadline'),
            request.form.get('event_detail')
        ))
        connection.commit()
        cur.close()
    
    # イベント一覧を取得（参加者数も含む）
    cur = connection.cursor()
    cur.execute("""
        SELECT e.event_id, e.event_name, e.event_date, e.event_time_start, 
               e.event_time_end, e.event_place, e.event_fee, e.event_member,
               e.event_deadline, f.uname as host_name,
               COUNT(ep.participant_id) as current_participants
        FROM events e
        JOIN flskauth f ON e.host_uid = f.uid
        LEFT JOIN event_participants ep ON e.event_id = ep.event_id 
                                        AND ep.status = 'registered'
        WHERE e.is_active = TRUE
        GROUP BY e.event_id, f.uname
        ORDER BY e.event_date ASC, e.event_time_start ASC
    """)
    events = cur.fetchall()
    cur.close()
    
    return render_template("event_list.html", events=events, uid=session["uid"], uname=session["uname"])

@app.route('/event_detail/<int:event_id>', methods=['GET', 'POST'])
def event_detail(event_id):
    if "uid" not in session:
        return redirect("./login")
    
    # POSTの場合は参加/キャンセル処理
    if request.method == 'POST':
        user_id = session["uid"]
        action = request.form.get('action')
        cur = connection.cursor()
        
        if action == 'join':
            # イベント情報を取得
            cur.execute("""
                SELECT event_member, 
                       COUNT(ep.participant_id) as current_participants
                FROM events e
                LEFT JOIN event_participants ep ON e.event_id = ep.event_id 
                                                AND ep.status = 'registered'
                WHERE e.event_id = %s AND e.is_active = TRUE
                GROUP BY e.event_id, e.event_member
            """, (event_id,))
            result = cur.fetchone()
            
            if result:
                max_participants, current_count = result[0], result[1]
                
                # 参加者数制限チェック
                if current_count < max_participants:
                    # 既存のレコードをチェック（すべてのステータス）
                    cur.execute("""
                        SELECT status FROM event_participants 
                        WHERE event_id = %s AND user_id = %s
                    """, (event_id, user_id))
                    existing_record = cur.fetchone()
                    
                    if existing_record:
                        # 既存のレコードがある場合
                        if existing_record[0] == 'cancelled':
                            # キャンセル状態のレコードを再アクティブ化
                            cur.execute("""
                                UPDATE event_participants 
                                SET status = 'registered', registered_at = CURRENT_TIMESTAMP
                                WHERE event_id = %s AND user_id = %s
                            """, (event_id, user_id))
                            connection.commit()
                        # 既に 'registered' の場合は何もしない
                    else:
                        # 新規参加登録
                        cur.execute("""
                            INSERT INTO event_participants (event_id, user_id) 
                            VALUES (%s, %s)
                        """, (event_id, user_id))
                        connection.commit()
        
        elif action == 'leave':
            # 参加登録を削除（論理削除）
            cur.execute("""
                UPDATE event_participants 
                SET status = 'cancelled' 
                WHERE event_id = %s AND user_id = %s AND status = 'registered'
            """, (event_id, user_id))
            connection.commit()
        
        cur.close()
        # POST処理後にGETリダイレクトしてページを再読み込み
        return redirect(request.url)
    
    cur = connection.cursor()
    # イベント詳細情報を取得
    cur.execute("""
        SELECT e.event_id, e.host_uid, e.event_name, e.event_date, 
               e.event_time_start, e.event_time_end, e.event_place, 
               e.event_fee, e.event_member, e.event_cancel, 
               e.event_cancel_case, e.event_deadline, e.event_detail,
               f.uname as host_name,
               COUNT(ep.participant_id) as current_participants
        FROM events e
        JOIN flskauth f ON e.host_uid = f.uid
        LEFT JOIN event_participants ep ON e.event_id = ep.event_id 
                                        AND ep.status = 'registered'
        WHERE e.event_id = %s AND e.is_active = TRUE
        GROUP BY e.event_id, e.host_uid, e.event_name, e.event_date,
                 e.event_time_start, e.event_time_end, e.event_place,
                 e.event_fee, e.event_member, e.event_cancel,
                 e.event_cancel_case, e.event_deadline, e.event_detail, f.uname
    """, (event_id,))
    event = cur.fetchone()
    
    if not event:
        cur.close()
        return "イベントが見つかりません", 404
    
    # 参加者一覧を取得
    cur.execute("""
        SELECT f.uname, ep.registered_at
        FROM event_participants ep
        JOIN flskauth f ON ep.user_id = f.uid
        WHERE ep.event_id = %s AND ep.status = 'registered'
        ORDER BY ep.registered_at ASC
    """, (event_id,))
    participants = cur.fetchall()
    
    # 現在のユーザーが参加済みかチェック
    cur.execute("""
        SELECT COUNT(*) FROM event_participants 
        WHERE event_id = %s AND user_id = %s AND status = 'registered'
    """, (event_id, session["uid"]))
    is_joined = cur.fetchone()[0] > 0
    
    cur.close()
    
    return render_template("event_detail.html", event=event, participants=participants, 
                         is_joined=is_joined, uid=session["uid"], uname=session["uname"])

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if "uid" not in session:
        return redirect("./login")
    
    cur = connection.cursor()
    
    # イベント情報を取得し、主催者チェック
    cur.execute("""
        SELECT * FROM events 
        WHERE event_id = %s AND host_uid = %s AND is_active = TRUE
    """, (event_id, session["uid"]))
    event = cur.fetchone()
    
    if not event:
        cur.close()
        return "イベントが見つからないか、編集権限がありません", 403
    
    if request.method == 'POST':
        # イベント情報を更新
        cur.execute("""
            UPDATE events SET 
                event_name = %s, event_date = %s, event_time_start = %s,
                event_time_end = %s, event_place = %s, event_fee = %s,
                event_member = %s, event_cancel = %s, event_cancel_case = %s,
                event_deadline = %s, event_detail = %s, updated_at = CURRENT_TIMESTAMP
            WHERE event_id = %s AND host_uid = %s
        """, (
            request.form.get('event_name'),
            request.form.get('event_date'),
            request.form.get('event_time_start'),
            request.form.get('event_time_end'),
            request.form.get('event_place'),
            request.form.get('event_fee'),
            request.form.get('event_member'),
            request.form.get('event_cancel'),
            request.form.get('event_cancel_case'),
            request.form.get('event_deadline'),
            request.form.get('event_detail'),
            event_id,
            session["uid"]
        ))
        connection.commit()
        cur.close()
        return redirect(f"../event_detail/{event_id}")
    
    cur.close()
    return render_template("./edit_event.html", event=event, uid=session["uid"], uname=session["uname"])

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if "uid" not in session:
        return redirect("./login")
    
    cur = connection.cursor()
    # 主催者チェック: イベントが存在し、現在のユーザーが主催者か確認
    cur.execute("SELECT host_uid FROM events WHERE event_id = %s", (event_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        return "イベントが見つかりません", 404

    host_uid = row[0]
    if host_uid != session["uid"]:
        cur.close()
        return "削除権限がありません", 403

    try:
        # 参加者データを先に削除
        cur.execute("DELETE FROM event_participants WHERE event_id = %s", (event_id,))
        # イベント本体を削除
        cur.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
        connection.commit()
    except Exception as e:
        # エラー時はロールバックしてエラーメッセージを返す
        connection.rollback()
        cur.close()
        return f"削除に失敗しました: {e}", 500

    cur.close()
    return redirect(url_for('event_list'))