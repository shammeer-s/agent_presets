import sys
import json
import os
import subprocess
import traceback

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugin.log")

def log(msg: str):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def execute_command(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()

def main():
    try:
        log("--- Execution Started ---")
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
        
        workspaces = payload.get("workspacePaths", [])
        target_dir = workspaces[0] if workspaces else os.getcwd()
        os.chdir(target_dir)
        log(f"Working directory set to: {target_dir}")
        
        execute_command(["git", "add", "."])
        status_output = execute_command(["git", "status", "--porcelain"])
        
        if not status_output:
            log("No changes detected.")
            print(json.dumps({"status": "skipped", "reason": "no_changes"}))
            return
            
        model_name = payload.get("activeModel", "Antigravity Agent")
        commit_message = f"chore(agent): auto-commit via {model_name}\n\nModified files:\n{status_output}"
        
        execute_command(["git", "commit", "-m", commit_message])
        log("Commit successful.")
        print(json.dumps({"status": "success", "commit_message": commit_message}))
        
    except Exception as e:
        log(f"Error: {str(e)}\n{traceback.format_exc()}")
        print(json.dumps({"status": "failed", "error": str(e)}))

if __name__ == "__main__":
    main()