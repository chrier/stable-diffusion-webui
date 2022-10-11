# 몰루 Web UI 설정
# 활성화 : True
# 비활성화 : False

class Config(object):
    # 본 설정들은 주의하여 설정하여야 합니다.
    pass_git_check = False   # 깃 관련 클론 절차를 건너뜁니다, 기본 : 비활성화(False)
    pass_model_check = False  # 모델 데이터 등을 확인하는 절차를 건너뜁니다, 기본 : 비활성화(False)
    pass_install_check = False   # 각종 필요 모듈 체크를 건너뜁니다.  기본 : 비활성화(False)

    # 본 설정들은 그림의 퀄리티와 연관 되어 있습니다.
    hypernetwork_enable = False  # Hyper Network 활성화, 기본 : 비활성화(False)
    v2_enable = False  # V2 활성화, 기본 : 비활성화(False)
    vae_enable = True  # VAE 활성화, 기본 : 활성화(True)
    yaml_enable = True  # YAML 설정 파일 로드, 기본 : 활성화(True)

    # Web UI 서버 관련 설정
    open_public = False  # 외부 접속 활성화, 기본 : 비활성화(False)
    server_port = 7860  # 서버 포트, 기본 : 7860
    disable_settings = False  # 설정 탭을 제거합니다, 기본 : 비활성화(False)
    
    deepdanbooru = True  # Deepdanbooru를 활성화합니다, 기본 : 활성화(True)