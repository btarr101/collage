import subprocess


def main() -> None:
    """
    executes a shell command
    """
    command = input("> ")
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError:
        pass


if __name__ == "__main__":
    main()
