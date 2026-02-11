# 배포 방법 상세 가이드

## 1. 사전 준비

### 네이버 클라우드 VPC 서버
- **사양**: 최소 2GB RAM, 20GB SSD
- **OS**: Ubuntu 20.04 LTS 이상 또는 Rocky Linux 8+
- **Python**: 3.8 이상
- **방화벽**: 22(SSH), 8000(API) 포트 개방

### MySQL
- MySQL 8.0 이상, 문자셋 utf8mb4, VPC 내부 접근 가능

### SSH
- root 또는 sudo 사용자, 22번 포트

---

## 2. 배포 실행

```bash
cd backend/actual
ls -la deploy.sh
bash deploy.sh   # Windows: Git Bash 또는 WSL
```

### 배포 스크립트 단계
1. VPC 배포 사전 체크  
2. 로컬 빌드 및 패키징  
3. VPC 서버 연결 테스트  
4. 프로젝트 디렉터리 생성  
5. 파일 업로드  
6. Python 환경 설정  
7. 환경 변수 설정  
8. systemd 서비스 파일 생성  
9. 서비스 활성화 및 시작  
10. 서비스 상태 확인  
11. 보안 설정  
12. 배포 완료  

---

## 3. 배포 후 확인

```bash
sudo systemctl status namdo-bot
sudo systemctl is-enabled namdo-bot
sudo journalctl -u namdo-bot -f
sudo journalctl -u namdo-bot --no-pager -n 100
curl http://localhost:8000/health
curl http://localhost:8000/docs
sudo netstat -tlnp | grep 8000
ps aux | grep namdo_bot
```

---

## 4. 서비스 관리

```bash
sudo systemctl start namdo-bot
sudo systemctl stop namdo-bot
sudo systemctl restart namdo-bot
sudo systemctl status namdo-bot
sudo systemctl enable namdo-bot
sudo systemctl disable namdo-bot
```

### 로그
```bash
sudo journalctl -u namdo-bot -f
sudo journalctl -u namdo-bot --since "2025-08-30 10:00:00"
sudo journalctl -u namdo-bot -p err
sudo journalctl --vacuum-time=30d
```

---

## 5. 문제 해결

### 서비스 시작 실패
- `sudo journalctl -u namdo-bot --no-pager -n 50`
- 가상환경·의존성: `ls /home/root/namdo-bot/venv/`, `pip list`
- `.env` 확인, DB 연결 테스트 (pymysql)

### 네트워크
- `ping`, `telnet ... 3306`, `ufw status`, ACG(22, 8000, 3306)

### 권한
- `ls -la /home/root/namdo-bot/`, `/etc/systemd/system/namdo-bot.service`

---

## 6. 모니터링·백업·업데이트

```bash
htop
df -h
ss -tuln
# 백업
mysqldump -h ... -u flova_user -p flova > backup_$(date +%Y%m%d).sql
tar -czf namdo-bot-backup-$(date +%Y%m%d).tar.gz /home/root/namdo-bot/
# 재배포
bash deploy.sh
pip install --upgrade -r requirements.txt
sudo systemctl restart namdo-bot
```

[← API 명세](04-api.md) | [메인 README](../README.md) | [다음: 환경 변수 →](06-environment.md)
