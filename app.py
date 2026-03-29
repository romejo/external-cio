import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, static_folder='.', template_folder='.')
CORS(app)

# DB 설정: Render 환경에서는 절대 경로를 사용하는 것이 안전합니다.
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'consulting.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 상담 내역 DB 모델
class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# DB 테이블 생성
with app.app_context():
    db.create_all()

# 메인 페이지 접속 시 index.html 반환
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# 정적 파일(이미지, CSS 등) 처리
@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('.', path)

# 상담 저장 API
@app.route('/api/consult', methods=['POST'])
def save_consultation():
    data = request.json
    try:
        new_entry = Consultation(
            name=data['name'],
            phone=data['phone'],
            message=data['message']
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 관리자 페이지
@app.route('/admin_joy_secure_925_check')
def admin_page():
    consultations = Consultation.query.order_by(Consultation.created_at.desc()).all()
    html = f"<html><body style='background:#180720;color:#f8dcff;padding:40px;'>"
    html += f"<h1>상담 내역 ({len(consultations)}건)</h1><table border='1' style='width:100%;border-collapse:collapse;'>"
    html += "<tr><th>날짜</th><th>이름</th><th>연락처</th><th>내용</th></tr>"
    for c in consultations:
        html += f"<tr><td>{c.created_at.strftime('%Y-%m-%d %H:%M')}</td><td>{c.name}</td><td>{c.phone}</td><td>{c.message}</td></tr>"
    html += "</table></body></html>"
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
