from shutil import copytree
from time import sleep, time
from pathlib import Path
from threading import Thread

class Watcher(Thread):
  def __init__(self, watchable_folder : Path, target_folder : Path):
    Thread.__init__(self)
    self.watchable_folder = watchable_folder
    self.target_folder = target_folder

  def copy_folder(self, source_path : Path, target_path: Path) -> None:
    target_path = target_path / source_path.stem
    ts = time()
    copytree(source_path,target_path)
    tf = time()
    print(f'Copy finished in {(tf-ts):.2f} seconds.')

  def is_part_file(self, _file : Path) -> bool:
    part_suffix = '.part'
    return _file.suffix.lower() == part_suffix

  def check_dir_in_progress(self, dir : Path) -> bool:
    for child in dir.iterdir():
      if child.is_file() and self.is_part_file(child):
        return True
      elif child.is_dir():
        return self.check_dir_in_progress(child)

    return False

  def is_in_progress(self, path : Path) -> bool:
    if path.is_dir():
      return self.check_dir_in_progress(path)

    return self.is_part_file(path)

  def run(self) -> None:
    print(f"I'm watching the folder: {self.watchable_folder}")
    while True:
      sleep(10)
      if not self.is_in_progress(self.watchable_folder):
        self.copy_folder(self.watchable_folder, self.target_folder)
        return

def start_watcher_thread(watchable_folder : Path, target_folder : Path) -> Watcher:
  watcher = Watcher(watchable_folder,target_folder)
  watcher.daemon = True
  watcher.start()
  return watcher

def check_valid_path(path : str,allow_empty : bool = False) -> bool:
  as_path_obj = Path(path).resolve()
  empty_path = Path('').resolve()
  return as_path_obj.exists and (allow_empty or as_path_obj != empty_path)

def get_paths(previous_target_folder : str = ''):
  while True:
    watch_folder = input('Folder to Watch: ')
    watch_folder = Path(watch_folder).resolve()

    if check_valid_path(watch_folder):
      break

    print("Folder don't exits!")
  
  while True:
    default_target = f'([Enter] to keep previous {previous_target_folder})' if check_valid_path(previous_target_folder) else ''
    target_folder = input(f'Target Folder{default_target}: ')
    target_folder = Path(target_folder if target_folder != '' else previous_target_folder).resolve()

    if check_valid_path(watch_folder,True):
      break

    print("Folder don't exits!")

  return (watch_folder, target_folder)

def print_help():
  print('Type [n] for a new Folder to watch. Ctrl+c or [x] to exit')

def main():
  option = ''
  target_folder = Path('').resolve()
  program_name = 'TorrentMover. Watches a folder and copy when it\'s finished.'
  lines = '='*len(program_name)
  print(lines, program_name, 'Press [h] for Help.', lines, sep='\n')
  while True:
    option = input('>>> ')
    if option.lower() == 'x':
      exit(0)
    elif option.lower() == 'n':
      default_path = Path('').resolve()
      watch_folder, target_folder = get_paths(str(target_folder) if target_folder != default_path else '')
    elif option.lower() == 'h':
      print_help()
      continue
    else:
      print('Option not recognized')
      continue
    
    start_watcher_thread(watch_folder,target_folder)


if __name__ == '__main__':
  try:
    main()
  except (KeyboardInterrupt, EOFError):
    exit(0)

