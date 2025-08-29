#!/bin/bash

# 남도봇 축제 추천 시스템 배포 스크립트
# 네이버 클라우드 VPC 서버에 배포

echo "🚀 남도봇 축제 추천 시스템 배포 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 설정 변수 (실제 값으로 수정 필요)
SERVER_IP="211.188.63.67"
SERVER_USER="root"
PROJECT_DIR="/home/$SERVER_USER/namdo-bot"
SERVICE_NAME="namdo-bot"

# 함수 정의
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 로컬 빌드 및 패키징
log_info "로컬 빌드 및 패키징 중..."
if ! python -m pip install -r requirements.txt; then
    log_error "의존성 설치 실패"
    exit 1
fi

# 2. 서버 연결 테스트
log_info "서버 연결 테스트 중..."
if ! ssh -o ConnectTimeout=10 $SERVER_USER@$SERVER_IP "echo 'Connection successful'"; then
    log_error "서버 연결 실패. IP 주소와 사용자명을 확인하세요."
    exit 1
fi

# 3. 서버에 프로젝트 디렉토리 생성
log_info "서버에 프로젝트 디렉토리 생성 중..."
ssh $SERVER_USER@$SERVER_IP "mkdir -p $PROJECT_DIR"

# 4. 파일 업로드
log_info "파일 업로드 중..."
scp -r ./* $SERVER_USER@$SERVER_IP:$PROJECT_DIR/

# 5. 서버에서 의존성 설치
log_info "서버에서 의존성 설치 중..."
ssh $SERVER_USER@$SERVER_IP "cd $PROJECT_DIR && python -m pip install -r requirements.txt"

# 6. 환경 변수 파일 설정
log_info "환경 변수 파일 설정 중..."
ssh $SERVER_USER@$SERVER_IP "cd $PROJECT_DIR && cp env_example.txt .env"

# 7. systemd 서비스 파일 생성
log_info "systemd 서비스 파일 생성 중..."
cat > /tmp/namdo-bot.service << EOF
[Unit]
Description=Namdo Bot Festival Recommendation System
After=network.target

[Service]
Type=simple
User=$SERVER_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=/usr/bin/python3 $PROJECT_DIR/namdo_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

scp /tmp/namdo-bot.service $SERVER_USER@$SERVER_IP:/tmp/
ssh $SERVER_USER@$SERVER_IP "sudo mv /tmp/namdo-bot.service /etc/systemd/system/"

# 8. 서비스 활성화 및 시작
log_info "서비스 활성화 및 시작 중..."
ssh $SERVER_USER@$SERVER_IP "sudo systemctl daemon-reload && sudo systemctl enable $SERVICE_NAME && sudo systemctl start $SERVICE_NAME"

# 9. 서비스 상태 확인
log_info "서비스 상태 확인 중..."
ssh $SERVER_USER@$SERVER_IP "sudo systemctl status $SERVICE_NAME --no-pager"

# 10. 방화벽 설정 (포트 8000 열기)
log_info "방화벽 설정 중..."
ssh $SERVER_USER@$SERVER_IP "sudo ufw allow 8000/tcp"

# 11. nginx 설정 (선택사항)
log_info "nginx 설정 중..."
cat > /tmp/namdo-bot-nginx << EOF
server {
    listen 80;
    server_name your-domain.com;  # 실제 도메인으로 수정

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

scp /tmp/namdo-bot-nginx $SERVER_USER@$SERVER_IP:/tmp/
ssh $SERVER_USER@$SERVER_IP "sudo mv /tmp/namdo-bot-nginx /etc/nginx/sites-available/namdo-bot && sudo ln -sf /etc/nginx/sites-available/namdo-bot /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl reload nginx"

# 12. 배포 완료
log_info "🎉 배포 완료!"
log_info "서비스 URL: http://$SERVER_IP:8000"
log_info "API 문서: http://$SERVER_IP:8000/docs"
log_info "상태 확인: sudo systemctl status $SERVICE_NAME"

# 13. 로그 확인 명령어 안내
echo ""
log_warn "로그 확인 명령어:"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo "  sudo tail -f /var/log/nginx/access.log"
echo ""
log_warn "서비스 재시작 명령어:"
echo "  sudo systemctl restart $SERVICE_NAME"
echo ""
log_warn "환경 변수 수정 후 재시작:"
echo "  sudo systemctl restart $SERVICE_NAME"
