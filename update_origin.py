import subprocess

def update_git_repo():
    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", "update origin"],
        ["git", "push", "origin", "main"]
    ]

    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        try:
            # check=True raises an exception if the command fails
            subprocess.run(cmd, check=True, text=True)
            print("Done.\n")
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}.")
            # A common error is committing with no changes; this stops the script
            print("Halting further execution.")
            break

if __name__ == "__main__":
    update_git_repo()