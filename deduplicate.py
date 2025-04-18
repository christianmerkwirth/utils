import os
import hashlib
import click


class Deduplicator:
    def __init__(self, path, dry_run=True):
        self.path = path
        self.file_dict = dict()
        self.dry_run = dry_run

    def deduplicate(self):
        self.get_files()
        self.clean_files()

    def get_file_hash(self, file_path):
        with open(file_path, "rb") as f:
            file = f.read()
            hash = hashlib.sha256(file).hexdigest()
            return hash

    def get_files(self):
        for file in os.listdir(self.path):
            full_path = os.path.join(self.path, file)
            if not os.path.isfile(full_path):
                continue
            file_size = os.path.getsize(full_path)
            hash = (file_size, self.get_file_hash(full_path))
            if not self.file_dict.get(hash):
                self.file_dict[hash] = list()
            self.file_dict[hash].append(file)

    def clean_files(self):
        for hash, file_names in self.file_dict.items():
            if len(file_names) <= 1:
                continue
            file_names.sort(reverse=True)
            files_to_delete = file_names[1:]
            print(f"File to keep: {file_names[0]}")
            print(f"Files to delete: {files_to_delete}")
            print("-" * 50)
            if not self.dry_run:
                for file in files_to_delete:
                    full_path = os.path.join(self.path, file)
                    print(f"...deleting: {full_path}")
                    os.remove(full_path)


@click.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    "--dry-run/--no-dry-run",
    default=True,
    help="Perform a dry run without deleting files (default: True)",
)
@click.option("--version", is_flag=True, help="Show version information")
def main(path, dry_run, version):
    """File deduplication tool that identifies and removes duplicate files.

    PATH is the directory to scan for duplicate files.

    The tool uses SHA-256 hashing to identify identical files and keeps the
    most recently named file (alphabetically) while marking others for deletion.
    """
    if version:
        print("File Deduplicator v0.1.0")
        return

    if not os.path.isdir(path):
        click.echo(f"Error: '{path}' is not a valid directory")
        return

    click.echo(f"Scanning directory: {path}")
    click.echo(f"Dry run: {dry_run}")

    d = Deduplicator(path, dry_run)
    d.deduplicate()


if __name__ == "__main__":
    main()
