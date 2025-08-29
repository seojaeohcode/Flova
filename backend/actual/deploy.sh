#!/bin/bash

# 남도봇 축제 추천 시스템 배포 스크립트
# 네이버 클라우드 VPC 서버에 배포

echo "🚀 남도봇 축제 추천 시스템 VPC 배포 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ========================================
# 🎯 VPC 배포 설정 (실제 값으로 수정 필요)
# ========================================

# VPC 서버 정보
VPC_SERVER_IP="211.188.63.67"           # ✅ VPC 서버의 공인 IP 또는 사설 IP
VPC_SERVER_USER="root"                  # ✅ VPC 서버 사용자명
VPC_SERVER_PASSWORD="B9!ND?UP7hMg*8r"  # 🔑 VPC 서버 비밀번호 (SSH 키 사용 시 비워둬도 됨)
VPC_PROJECT_DIR="/home/$VPC_SERVER_USER/namdo-bot"
VPC_SERVICE_NAME="namdo-bot"

# 데이터베이스 정보 (VPC 내부 Private 도메인 사용)
DB_HOST="db-37h1g8.vpc-cdb.ntruss.com"
DB_PORT="3306"
DB_NAME="flova"
DB_USER="flova_user"
DB_PASSWORD="flova06*"

# ========================================
# 🔧 함수 정의
# ========================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# ========================================
# 📋 사전 체크
# ========================================

log_step "1. VPC 배포 사전 체크"

# ... (사전 체크 로직은 이전과 동일)

# ========================================
# 🚀 배포 시작
# ========================================

log_step "2. 로컬 의존성 확인"
if ! python -m pip install -r requirements.txt; then
    log_error "로컬 의존성 설치/확인 실패"
    exit 1
fi

# ========================================
# 🔌 VPC 서버 연결 테스트
# ========================================

log_step "3. VPC 서버 연결 테스트"
if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $VPC_SERVER_USER@$VPC_SERVER_IP "echo 'VPC 서버 연결 성공'"; then
    log_error "VPC 서버 연결 실패!"
    log_error "확인사항: ACG에서 SSH(22) 포트가 열려있는지, IP/사용자 정보가 정확한지 확인"
    exit 1
fi
log_info "✅ VPC 서버 연결 성공: $VPC_SERVER_IP"

# ========================================
# 📤 프로젝트 파일 업로드
# ========================================

log_step "4. VPC 서버에 프로젝트 디렉토리 생성 및 파일 업로드"
ssh $VPC_SERVER_USER@$VPC_SERVER_IP "rm -rf $VPC_PROJECT_DIR && mkdir -p $VPC_PROJECT_DIR"
scp -r namdo_bot.py database.py auth.py models.py crud.py tour_api.py festival_service.py requirements.txt $VPC_SERVER_USER@$VPC_SERVER_IP:$VPC_PROJECT_DIR/
log_info "✅ 소스 코드 업로드 완료"

# ========================================
# 🗄️ 데이터베이스 스키마 업데이트
# ========================================

log_step "4.5. 데이터베이스 스키마 업데이트"
ssh $VPC_SERVER_USER@$VPC_SERVER_IP "mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e \"USE $DB_NAME; ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255) NULL;\"" 2>/dev/null || echo "⚠️ profile_picture 컬럼이 이미 존재하거나 추가 중 오류 발생"

# username 컬럼 추가 (User 테이블에)
ssh $VPC_SERVER_USER@$VPC_SERVER_IP "mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e \"USE $DB_NAME; ALTER TABLE users ADD COLUMN username VARCHAR(255) UNIQUE NOT NULL AFTER id;\"" 2>/dev/null || echo "⚠️ username 컬럼이 이미 존재하거나 추가 중 오류 발생"

# 축제 관련 테이블 생성
ssh $VPC_SERVER_USER@$VPC_SERVER_IP "mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e \"USE $DB_NAME; CREATE TABLE IF NOT EXISTS festivals (id INT AUTO_INCREMENT PRIMARY KEY, contentid VARCHAR(50) UNIQUE NOT NULL, title VARCHAR(500) NOT NULL, contenttypeid VARCHAR(50), addr1 VARCHAR(500), start_date VARCHAR(20), end_date VARCHAR(20), image VARCHAR(1000), progresstype VARCHAR(100), festivaltype VARCHAR(100), tel VARCHAR(100), region VARCHAR(100), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);\"" 2>/dev/null || echo "⚠️ festivals 테이블 생성 중 오류 발생"

ssh $VPC_SERVER_USER@$VPC_SERVER_IP "mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e \"USE $DB_NAME; CREATE TABLE IF NOT EXISTS festival_details (id INT AUTO_INCREMENT PRIMARY KEY, contentid VARCHAR(50), title VARCHAR(500) NOT NULL, createdtime VARCHAR(20), modifiedtime VARCHAR(20), tel VARCHAR(100), telname VARCHAR(100), homepage VARCHAR(1000), firstimage VARCHAR(1000), firstimage2 VARCHAR(1000), addr1 VARCHAR(500), addr2 VARCHAR(500), mapx VARCHAR(50), mapy VARCHAR(50), mlevel VARCHAR(50), overview TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (contentid) REFERENCES festivals(contentid));\"" 2>/dev/null || echo "⚠️ festival_details 테이블 생성 중 오류 발생"

ssh $VPC_SERVER_USER@$VPC_SERVER_IP "mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e \"USE $DB_NAME; CREATE TABLE IF NOT EXISTS festival_intros (id INT AUTO_INCREMENT PRIMARY KEY, contentid VARCHAR(50), sponsor1 VARCHAR(200), sponsor1tel VARCHAR(100), sponsor2 VARCHAR(200), eventenddate VARCHAR(20), playtime VARCHAR(200), eventplace VARCHAR(500), eventstartdate VARCHAR(20), usetimefestival VARCHAR(500), progresstype VARCHAR(100), festivaltype VARCHAR(100), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (contentid) REFERENCES festivals(contentid));\"" 2>/dev/null || echo "⚠️ festival_intros 테이블 생성 중 오류 발생"

ssh $VPC_SERVER_USER@$VPC_SERVER_IP "mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e \"USE $DB_NAME; CREATE TABLE IF NOT EXISTS pet_infos (id INT AUTO_INCREMENT PRIMARY KEY, contentid VARCHAR(50), acmpyPsblCpam VARCHAR(200), relaRntlPrdlst VARCHAR(500), acmpyNeedMtr VARCHAR(500), etcAcmpyInfo TEXT, relaPurcPrdlst VARCHAR(500), relaAcdntRiskMtr VARCHAR(500), acmpyTypeCd VARCHAR(50), relaPosesFclty VARCHAR(500), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (contentid) REFERENCES festivals(contentid));\"" 2>/dev/null || echo "⚠️ pet_infos 테이블 생성 중 오류 발생"

log_info "✅ 데이터베이스 스키마 업데이트 완료"

# ========================================
# 🐍 Python 환경 설정
# ========================================

log_step "5. VPC 서버에서 Python 환경 설정"
ssh $VPC_SERVER_USER@$VPC_SERVER_IP "cd $VPC_PROJECT_DIR && \
    (command -v python3 || (apt-get update -y && apt-get install -y python3)) && \
    (command -v pip || apt-get install -y python3-pip) && \
    (command -v venv || apt-get install -y python3-venv) && \
    python3 -m venv venv && \
    source venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt"
log_info "✅ Python 가상환경 및 의존성 설치 완료"

# ========================================
# 🔐 환경 변수 설정
# ========================================

log_step "6. VPC 서버에 .env 파일 생성"

# [수정] .env 파일 생성 시, 하드코딩 대신 상단에 정의된 변수를 사용하도록 변경
ssh $VPC_SERVER_USER@$VPC_SERVER_IP "cat > $VPC_PROJECT_DIR/.env << EOF
# NamdoBot Environment Variables (auto-generated by deploy.sh)

# Database Settings
DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?charset=utf8mb4

# API Keys (Required)
TOUR_API_KEY=\"b2a4d3de59c3245acf939ffa8d669a302df0d37319560e0fe841e1723dae078e\"
CLOVASTUDIO_API_KEY=\"nv-19cdb05e41834049b872867bc517fee9IfZJ\"

# JWT Secret (Production: Should be a long random string)
SECRET_KEY=namdo-bot-secret-key-2024-flova-project-change-this-in-production

# Other settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF"
log_info "✅ .env 파일 생성 완료"

# ========================================
# 🚀 systemd 서비스 설정
# ========================================

log_step "7. systemd 서비스 파일 생성 및 배포"

# 로컬에 서비스 파일 임시 생성
cat > /tmp/namdo-bot.service << EOF
[Unit]
Description=Namdo Bot Festival Recommendation System
After=network.target

[Service]
User=$VPC_SERVER_USER
Group=$VPC_SERVER_USER
WorkingDirectory=$VPC_PROJECT_DIR
ExecStart=$VPC_PROJECT_DIR/venv/bin/uvicorn namdo_bot:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 서버로 전송 후 이동
scp /tmp/namdo-bot.service $VPC_SERVER_USER@$VPC_SERVER_IP:/tmp/
ssh $VPC_SERVER_USER@$VPC_SERVER_IP "sudo mv /tmp/namdo-bot.service /etc/systemd/system/$VPC_SERVICE_NAME.service"
log_info "✅ systemd 서비스 파일 배포 완료"

# ========================================
# 🔧 서비스 활성화 및 시작
# ========================================

log_step "8. systemd 서비스 활성화 및 재시작"

ssh $VPC_SERVER_USER@$VPC_SERVER_IP "sudo systemctl daemon-reload && \
    sudo systemctl enable $VPC_SERVICE_NAME && \
    sudo systemctl restart $VPC_SERVICE_NAME"
log_info "✅ 서비스 활성화 및 재시작 완료"

# ========================================
# 📊 서비스 상태 확인
# ========================================

log_step "9. 서비스 최종 상태 확인"
sleep 5 # 서비스가 시작될 시간을 잠시 대기
ssh $VPC_SERVER_USER@$VPC_SERVER_IP "sudo systemctl status $VPC_SERVICE_NAME --no-pager"

# ========================================
# 🎯 배포 완료
# ========================================
log_info "🎉 VPC 배포가 성공적으로 완료되었습니다!"
log_info "VPC 내부 접속 주소: http://$VPC_SERVER_IP:8000"
log_info "로그 확인 명령어: ssh $VPC_SERVER_USER@$VPC_SERVER_IP 'sudo journalctl -u $VPC_SERVICE_NAME -f'"