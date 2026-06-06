import sys
import json
import os
import subprocess

def execute_command(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def main():
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input else {}
        
        workspaces = payload.get("workspacePaths", [os.getcwd()])
        os.chdir(workspaces[0])
        
        model_name = payload.get("activeModel", "Antigravity Agent")
        
        execute_command(["git", "add", "."])
        
        status_output = subprocess.run(
            ["git", "status", "--porcelain"], 
            capture_output=True, 
            text=True
        ).stdout.strip()
        
        if not status_output:
            print(json.dumps({"status": "skipped", "reason": "no_changes"}))
            return
            
        commit_message = f"chore(agent): auto-commit via {model_name}\n\nModified files:\n{status_output}"
        
        execute_command(["git", "commit", "-m", commit_message])
        print(json.dumps({"status": "success", "commit_message": commit_message}))
        
    except Exception as e:
        print(json.dumps({"status": "failed", "error": str(e)}))

if __name__ == "__main__":
    main()