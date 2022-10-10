# 몰루 Web UI 설정
# 활성화 : True
# 비활성화 : False

class Config(object):
    v2_enable = False  # V2 활성화, 기본 : 비활성화(False)
    vae_enable = True  # VAE 활성화, 기본 : 활성화(True)
    open_public = False  # 외부 접속 활성화, 기본 : 비활성화(False)
    server_port = 7860  # 서버 포트, 기본 : 7860
    remove_while = True  # 불 필요한 반복문 제거, 기본 : 활성화(True)