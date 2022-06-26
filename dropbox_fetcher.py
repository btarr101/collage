from pathlib import Path

import dropbox
import dropbox.exceptions
from defopt import run
from progressbar import progressbar


class DropboxFetcher:
    """
    Class that fetches images from a dropbox account.
    """

    def __init__(self, access_token: str, dbx_image_dir: Path):
        """
        Constructs a new instance that fetches using a specific access token.

        :param access_token: the oauth2 token needed to access the particular dropbox.
        :param dbx_image_dir: the directory within the dropbox with the images to fetch.
        """
        self.dbx = dropbox.Dropbox(oauth2_access_token=access_token)
        self.dbx_image_dir = dbx_image_dir

        # fixing up the path for dropbox
        if str(self.dbx_image_dir)[0] != '/':
            self.dbx_image_dir = Path('/' + str(self.dbx_image_dir))

    def fetch_to_dir(self, local_image_dir: Path) -> None:
        """
        Fetches images from a dropbox to a local directory.

        :param local_image_dir: the local directory to fetch to.
        """

        # noinspection PyTypeChecker
        filenames = [file.name for file in self.dbx.files_list_folder(str(self.dbx_image_dir)).entries]
        for filename in progressbar(filenames):
            try:
                self.dbx.files_download_to_file(
                    str(local_image_dir / filename),
                    str(self.dbx_image_dir / filename)
                )
            except dropbox.exceptions.DropboxException as err:
                print(f"\t-> !Error: {err}, stopping...")
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


if __name__ == "__main__":
    run(main)
