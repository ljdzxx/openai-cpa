import json
import re
import shutil
import subprocess
from pathlib import Path


JSON_PATH = Path("fly_batch_deploy.json")
FLY_TOML_PATH = Path("fly.toml")


def run_deploy_command(cmd: str, app: str) -> None:
    exe_path = shutil.which(cmd)
    if exe_path:
        subprocess.run([exe_path, "deploy", "--ha=false", "-a", app], check=True)
        return

    powershell_exe = shutil.which("pwsh") or shutil.which("powershell")
    if not powershell_exe:
        raise FileNotFoundError(
            f"Command '{cmd}' was not found, and neither 'pwsh' nor 'powershell' is available."
        )

    ps_command = f"& {cmd} deploy --ha=false -a {app}"
    subprocess.run([powershell_exe, "-Command", ps_command], check=True)


def main() -> None:
    entries = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    for entry in entries:
        app = entry["app"]
        region = entry["region"]
        cmd = entry["cmd"]

        content = FLY_TOML_PATH.read_text(encoding="utf-8")
        content = re.sub(
            r'^(app\s*=\s*).*$',
            rf'\1"{app}"',
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            r'^(primary_region\s*=\s*).*$',
            rf'\1"{region}"',
            content,
            flags=re.MULTILINE,
        )

        FLY_TOML_PATH.write_text(content, encoding="utf-8", newline="\n")

        print(f"Deploying cmd={cmd} app={app} region={region}")
        run_deploy_command(cmd, app)


if __name__ == "__main__":
    main()
