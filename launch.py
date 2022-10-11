# this scripts installs necessary requirements and launches main program in webui.py
import subprocess
import os
import sys
import importlib.util
import shlex
import platform
import molru_config
import time
im_norhu1130 = """
                                     #     #    #####    ###   
#    #  ####  #####  #    # #    #  ##    ##   #     #  #   #  
##   # #    # #    # #    # #    # # #   # #         # #     # 
# #  # #    # #    # ###### #    #   #     #    #####  #     # 
#  # # #    # #####  #    # #    #   #     #         # #     # 
#   ## #    # #   #  #    # #    #   #     #   #     #  #   #  
#    #  ####  #    # #    #  ####  ##### #####  #####    ###   
"""
from_arcalive = """
  ##   #####   ####    ##      #      # #    # ###### 
 #  #  #    # #    #  #  #     #      # #    # #      
#    # #    # #      #    #    #      # #    # #####  
###### #####  #      ######    #      # #    # #      
#    # #   #  #    # #    #    #      #  #  #  #      
#    # #    #  ####  #    #    ###### #   ##   ###### 
"""
dir_repos = "repositories"
python = sys.executable
git = os.environ.get('GIT', "git")

def check_empty_dir(dir,fileEx):
    if not os.path.exists(dir):
        os.makedirs(dir)
    if [file for file in os.listdir(dir) if file.endswith(fileEx)] == []:
        return True
    return False

def download_file(url, save_dir):
    import requests
    from tqdm import tqdm
    response = requests.get(url, stream=True)
    total_size_in_bytes= int(response.headers.get('content-length', 0))
    block_size = 1024 # 1 KB
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(save_dir, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()

def model_data_checker():
    if not os.path.exists(os.path.abspath("models/Stable-diffusion")):
        os.makedirs(os.path.abspath("models/Stable-diffusion"))
    Dir = f'{os.path.abspath("models/Stable-diffusion")}'
    if check_empty_dir(Dir,r'.ckpt'):
        print("[ 몰루 Web UI ] 모델 파일을 찾을 수 없습니다.")
        print("미러서버에서 다운로드 합니다.")
        download_file("http://protect.norhu1130.tech:8000/model","models/Stable-diffusion/animefull-final-pruned.ckpt")
    else:
        print("[ 몰루 Web UI ] 모델 데이터가 확인되었습니다.")

    if molru_config.Config.yaml_enable:
        if check_empty_dir(Dir,r'.yaml'):
            print("YAML이 활성화 되었으나, 찾지 못했습니다.")
            print("미러서버에서 다운로드 합니다.")
            download_file("http://protect.norhu1130.tech:8000/yaml","models/Stable-diffusion/animefull-final-pruned.yaml")
        else: print("[ 몰루 Web UI ] YAML 데이터가 확인되었습니다.")

    if molru_config.Config.vae_enable:
        if check_empty_dir(Dir,r'.vae.pt'):
            print("VAE가 활성화 되었으나, 찾지 못했습니다.")
            print("미러서버에서 다운로드 합니다.")
            download_file("http://protect.norhu1130.tech:8000/vae","models/Stable-diffusion/animefull-final-pruned.vae.pt")
        else: print("[ 몰루 Web UI ] VAE 데이터가 확인되었습니다.")

def v2_data_checker():
    if not os.path.exists("v2.pt"):
        print("[ 몰루 Web UI ] V2 파일을 찾을 수 없습니다.")
        print("다운로드 중 입니다.")
        download_file("http://protect.norhu1130.tech:8000/v2","v2.pt")
        return

def extract_arg(args, name):
    return [x for x in args if x != name], name in args


def run(command, desc=None, errdesc=None):
    if desc is not None:
        print(desc)

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    if result.returncode != 0:

        message = f"""{errdesc or 'Error running command'}.
Command: {command}
Error code: {result.returncode}
stdout: {result.stdout.decode(encoding="utf8", errors="ignore") if len(result.stdout)>0 else '<empty>'}
stderr: {result.stderr.decode(encoding="utf8", errors="ignore") if len(result.stderr)>0 else '<empty>'}
"""
        raise RuntimeError(message)

    return result.stdout.decode(encoding="utf8", errors="ignore")


def check_run(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return result.returncode == 0


def is_installed(package):
    try:
        spec = importlib.util.find_spec(package)
    except ModuleNotFoundError:
        return False

    return spec is not None


def repo_dir(name):
    return os.path.join(dir_repos, name)


def run_python(code, desc=None, errdesc=None):
    return run(f'"{python}" -c "{code}"', desc, errdesc)


def run_pip(args, desc=None):
    return run(f'"{python}" -m pip {args} --prefer-binary', desc=f"{desc} 모듈을 설치 중!", errdesc=f"{desc} 모듈 설치 실패..")


def check_run_python(code):
    return check_run(f'"{python}" -c "{code}"')


def git_clone(url, dir, name, commithash=None):
    # TODO clone into temporary dir and move if successful

    if os.path.exists(dir):
        if commithash is None:
            return

        current_hash = run(f'"{git}" -C {dir} rev-parse HEAD', None, f"Couldn't determine {name}'s hash: {commithash}").strip()
        if current_hash == commithash:
            return

        run(f'"{git}" -C {dir} fetch', f"Fetching updates for {name}...", f"Couldn't fetch {name}")
        run(f'"{git}" -C {dir} checkout {commithash}', f"Checking out commint for {name} with hash: {commithash}...", f"Couldn't checkout commit {commithash} for {name}")
        return

    run(f'"{git}" clone "{url}" "{dir}"', f"Cloning {name} into {dir}...", f"Couldn't clone {name}")

    if commithash is not None:
        run(f'"{git}" -C {dir} checkout {commithash}', None, "Couldn't checkout {name}'s hash: {commithash}")


def prepare_enviroment():
    torch_command = os.environ.get('TORCH_COMMAND', "pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113")
    requirements_file = os.environ.get('REQS_FILE', "requirements_versions.txt")
    commandline_args = os.environ.get('COMMANDLINE_ARGS', "")

    gfpgan_package = os.environ.get('GFPGAN_PACKAGE', "git+https://github.com/TencentARC/GFPGAN.git@8d2447a2d918f8eba5a4a01463fd48e45126a379")
    clip_package = os.environ.get('CLIP_PACKAGE', "git+https://github.com/openai/CLIP.git@d50d76daa670286dd6cacf3bcd80b5e4823fc8e1")

    stable_diffusion_commit_hash = os.environ.get('STABLE_DIFFUSION_COMMIT_HASH', "69ae4b35e0a0f6ee1af8bb9a5d0016ccb27e36dc")
    taming_transformers_commit_hash = os.environ.get('TAMING_TRANSFORMERS_COMMIT_HASH', "24268930bf1dce879235a7fddd0b2355b84d7ea6")
    k_diffusion_commit_hash = os.environ.get('K_DIFFUSION_COMMIT_HASH', "f4e99857772fc3a126ba886aadf795a332774878")
    codeformer_commit_hash = os.environ.get('CODEFORMER_COMMIT_HASH', "c5b4593074ba6214284d6acd5f1719b6c5d739af")
    blip_commit_hash = os.environ.get('BLIP_COMMIT_HASH', "48211a1594f1321b00f14c9f7a5b4813144b2fb9")

    args = shlex.split(commandline_args)

    args, skip_torch_cuda_test = extract_arg(args, '--skip-torch-cuda-test')
    xformers = '--xformers' in args
    deepdanbooru = molru_config.Config().deepdanbooru
    ngrok = '--ngrok' in args

    try:
        commit = run(f"{git} rev-parse HEAD").strip()
        current_hash = run(f'"{git}" rev-parse HEAD', None, f"커밋 해쉬 가져오기 실패..").strip()
        if not current_hash == commit:
            print("[ ! ] 현재 구버전을 쓰고 있는것 같아요.")
            print("일부 문제가 발생할 수 있어요!")
            time.sleep(1.5)
    except Exception:
        commit = "<none>"
        print("[ ! ] 이런! 무언가 문제가 발생하였어요.")
        print("커밋 정보를 가져올 수 없어요.")
        print("이 문제가 계속 발생한다면, 이슈를 올려주세요.")
        os.exit(1)
    print(im_norhu1130)
    print(from_arcalive)
    print("="*75)
    print(f"{' '*32}몰루 Web UI")
    print("="*75)
    print("수정 : 아카라이브 @norhu1130")
    print(f"Python {sys.version}")
    print(f"Git 커밋 해시 : {commit}")
    if not molru_config.Config().pass_git_check:
        os.makedirs(dir_repos, exist_ok=True)

        git_clone("https://github.com/CompVis/stable-diffusion.git", repo_dir('stable-diffusion'), "Stable Diffusion", stable_diffusion_commit_hash)
        git_clone("https://github.com/CompVis/taming-transformers.git", repo_dir('taming-transformers'), "Taming Transformers", taming_transformers_commit_hash)
        git_clone("https://github.com/crowsonkb/k-diffusion.git", repo_dir('k-diffusion'), "K-diffusion", k_diffusion_commit_hash)
        git_clone("https://github.com/sczhou/CodeFormer.git", repo_dir('CodeFormer'), "CodeFormer", codeformer_commit_hash)
        git_clone("https://github.com/salesforce/BLIP.git", repo_dir('BLIP'), "BLIP", blip_commit_hash)

    if not molru_config.Config.pass_install_check:
        print("설치된 모듈을 확인하고 있습니다.")
        if not is_installed("torch") or not is_installed("torchvision"):
            run(f'"{python}" -m {torch_command}', "Torch를 설치 중.. [ 종료하지 말고 기다려 주세요. ]", "Torch를 설치하지 못했어요.")

        if not is_installed("gfpgan"):
            run_pip(f"install {gfpgan_package}", "gfpgan")

        if not is_installed("requests"):
            run_pip(f"install requests", "requests")

        if not is_installed("tqdm"):
            run_pip(f"install tqdm", "tqdm")

        if not is_installed("clip"):
            run_pip(f"install {clip_package}", "clip")

        if not is_installed("xformers") and xformers and platform.python_version().startswith("3.10"):
            if platform.system() == "Windows":
                run_pip("install https://github.com/C43H66N12O12S2/stable-diffusion-webui/releases/download/c/xformers-0.0.14.dev0-cp310-cp310-win_amd64.whl", "xformers")
            elif platform.system() == "Linux":
                run_pip("install xformers", "xformers")

        if not is_installed("deepdanbooru") and deepdanbooru:
            run_pip("install git+https://github.com/KichangKim/DeepDanbooru.git@edf73df4cdaeea2cf00e9ac08bd8a9026b7a7b26#egg=deepdanbooru[tensorflow] tensorflow==2.10.0 tensorflow-io==0.27.0", "deepdanbooru")

        if not is_installed("lpips"):
            run_pip(f"install -r {os.path.join(repo_dir('CodeFormer'), 'requirements.txt')}", "CodeFormer 필요 모듈")
        run_pip(f"install -r {requirements_file}", "Web UI 필요 모듈")
        if not is_installed("gfpgan"):
            run_pip(f"install {gfpgan_package}", "gfpgan")

        if not is_installed("clip"):
            run_pip(f"install {clip_package}", "clip")

        if not is_installed("xformers") and xformers and platform.python_version().startswith("3.10"):
            if platform.system() == "Windows":
                run_pip("install https://github.com/C43H66N12O12S2/stable-diffusion-webui/releases/download/c/xformers-0.0.14.dev0-cp310-cp310-win_amd64.whl", "xformers")
            elif platform.system() == "Linux":
                run_pip("install xformers", "xformers")

        if not is_installed("deepdanbooru") and deepdanbooru:
            run_pip("install git+https://github.com/KichangKim/DeepDanbooru.git@edf73df4cdaeea2cf00e9ac08bd8a9026b7a7b26#egg=deepdanbooru[tensorflow] tensorflow==2.10.0 tensorflow-io==0.27.0", "deepdanbooru")

        if not is_installed("pyngrok") and ngrok:
            run_pip("install pyngrok", "ngrok")

    if not skip_torch_cuda_test:
        run_python("import torch; assert torch.cuda.is_available(), 'Torch is not able to use GPU; add --skip-torch-cuda-test to COMMANDLINE_ARGS variable to disable this check'")
    if not molru_config.Config().pass_model_check:
        print("[ 몰루 Web UI ] 모델 데이터를 확인 중 입니다.")
        model_data_checker()
    if molru_config.Config.v2_enable:
        print("[ 몰루 Web UI ] V2 데이터를 확인 중 입니다.")
        v2_data_checker()

    os.makedirs(dir_repos, exist_ok=True)

    git_clone("https://github.com/CompVis/stable-diffusion.git", repo_dir('stable-diffusion'), "Stable Diffusion", stable_diffusion_commit_hash)
    git_clone("https://github.com/CompVis/taming-transformers.git", repo_dir('taming-transformers'), "Taming Transformers", taming_transformers_commit_hash)
    git_clone("https://github.com/crowsonkb/k-diffusion.git", repo_dir('k-diffusion'), "K-diffusion", k_diffusion_commit_hash)
    git_clone("https://github.com/sczhou/CodeFormer.git", repo_dir('CodeFormer'), "CodeFormer", codeformer_commit_hash)
    git_clone("https://github.com/salesforce/BLIP.git", repo_dir('BLIP'), "BLIP", blip_commit_hash)

    if not is_installed("lpips"):
        run_pip(f"install -r {os.path.join(repo_dir('CodeFormer'), 'requirements.txt')}", "requirements for CodeFormer")

    run_pip(f"install -r {requirements_file}", "requirements for Web UI")

    sys.argv += args
    import torch

    print(f"GPU : {torch.cuda.get_device_name(0)}")

    if '--precision full' not in sys.argv and '--no-half' not in sys.argv:
        if str(torch.cuda.get_device_name(0)).startswith("NVIDIA GeForce GTX 16"):
            print("! GTX 16XX을 감지했습니다.")
            print("자동적으로 오류 수정 옵션을 적용합니다.")

            sys.argv += '--no-half'.split()
            sys.argv += '--precision full'.split()

    if '--xformers' not in sys.argv:
        if str(torch.cuda.get_device_name(0)).startswith("NVIDIA GeForce RTX 30"):
            print("! GTX 30XX을 감지했습니다.")
            print("자동적으로 최적화 옵션을 적용합니다.")

            sys.argv += '--xformers'.split()

    if "--exit" in args:
        print("Exiting because of --exit argument")
        exit(0)

def start_webui():
    print(f"Web UI를 시작 중... 매개 변수 : {' '.join(sys.argv[1:])}")
    import webui
    webui.webui()

if __name__ == "__main__":
    prepare_enviroment()
    start_webui()
