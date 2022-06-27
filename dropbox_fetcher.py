import os
import sys
from pathlib import Path

import dropbox
import dropbox.exceptions
from defopt import run
from progressbar import progressbar


class DropboxFetcher:
    """
    Class that fetches files from a dropbox account.
    """

    def __init__(self, access_token: str, dbx_dir: Path):
        """
        Constructs a new instance that fetches using a specific access token.

        :param access_token: the oauth2 token needed to access the particular dropbox.
        :param dbx_dir: the directory within the dropbox with the files to fetch.
        """
        self.dbx = dropbox.Dropbox(oauth2_access_token=access_token)
        self.dbx_dir = dbx_dir

        # fixing up the path for dropbox
        if str(self.dbx_dir)[0] != '/':
            self.dbx_dir = Path('/' + str(self.dbx_dir))

    def fetch_to_dir(self, local_dir: Path) -> None:
        """
        Fetches files from a dropbox to a local directory.

        :param local_dir: the local directory to fetch to.
        """

        # noinspection PyTypeChecker
        filenames = [file.name for file in self.dbx.files_list_folder(str(self.dbx_dir)).entries]
        user = self.dbx.users_get_current_account().name.display_name

        print(f"Downloading images from {user}'s dropbox ({self.dbx_dir}) to {local_dir}.")
        for filename in progressbar(filenames):
            try:
                self.dbx.files_download_to_file(
                    str(local_dir / filename),
                    str(self.dbx_dir / filename)
                )
            except dropbox.exceptions.DropboxException as err:
                print(f"Error: {err}, stopping...")
                return


def main(*, token: str, remote_dir: Path, local_dir: Path = None):
    """
    Fetches data from a dropbox folder.

    :param token: the oauth2 token for dropbox.
    :param remote_dir: the remote directory in a dropbox.
    :param local_dir: the local directory to download to.
    """

    if local_dir is None:
        local_dir = remote_dir

    if not local_dir.exists():
        local_dir.mkdir(parents=True)

    fetcher = DropboxFetcher(token, remote_dir)
    fetcher.fetch_to_dir(local_dir)

    if len(os.listdir(local_dir)) < 1:
        print("Error: No files were downloaded.")
        sys.exit()


if __name__ == "__main__":
    run(main)
