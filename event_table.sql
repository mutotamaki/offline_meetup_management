-- オフ会情報を格納するテーブル
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    host_uid INTEGER NOT NULL,  -- 主催者のユーザーID（flskauthテーブルのuidと関連）
    event_name TEXT NOT NULL,
    event_date DATE NOT NULL,
    event_time_start TIME NOT NULL,
    event_time_end TIME NOT NULL,
    event_place TEXT NOT NULL,
    event_fee INTEGER DEFAULT 0,  -- 参加費（円）
    event_member INTEGER NOT NULL,  -- 募集人数
    event_cancel DATE,  -- キャンセル期限
    event_cancel_case TEXT,  -- 中止の場合の対応
    event_deadline DATE NOT NULL,  -- 募集締切
    event_detail TEXT,  -- 詳細説明
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 作成日時
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新日時
    is_active BOOLEAN DEFAULT TRUE  -- アクティブフラグ（削除フラグの代替）
) WITHOUT OIDS;

-- オフ会参加者を管理するテーブル
CREATE TABLE event_participants (
    participant_id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,  -- 参加者のユーザーID（flskauthテーブルのuidと関連）
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 参加登録日時
    status VARCHAR(20) DEFAULT 'registered',  -- 参加ステータス（registered, cancelled, etc.）
    UNIQUE(event_id, user_id)  -- 同じイベントに同じユーザーが重複登録することを防ぐ
) WITHOUT OIDS;

-- インデックスの作成（検索性能向上のため）
CREATE INDEX idx_events_host_uid ON events(host_uid);
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_deadline ON events(event_deadline);
CREATE INDEX idx_event_participants_event_id ON event_participants(event_id);
CREATE INDEX idx_event_participants_user_id ON event_participants(user_id);