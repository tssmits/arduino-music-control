import csv
import os

def get_item_for_qr_code(msg, csv_filename='map.csv'):
  with open(csv_filename, 'r') as csvfile:
    mapreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in mapreader:
      if row[0] == msg:
        return {
          'key': row[0],
          'type': row[1],
          'uri': row[2]
        }

  return None

def all_music_files_in_directory(rootDir):
  for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
    for fname in sorted(fileList):
        fn = os.path.join(dirName, fname)
        ext = os.path.splitext(fn)[-1].lower()
        if ext in ['.mp3', '.flac', '.wav', '.ogg']:
          yield fn

if __name__ == '__main__':
  print("Testing get_item_for_qr_code...")
  print(get_item_for_qr_code('QR-Code:HiddenOrchestra-Archipelago'))
  print(get_item_for_qr_code('QR-Code:Pearl Jam - Ten'))
  print(get_item_for_qr_code('QR-Code:nonexistant'))

  print("Testing all_music_files_in_directory...")
  for a in all_music_files_in_directory('/media/pi/LACIE/music/Storage2/audio/Zzz - 2008 - Running With The Beast'):
    print(a)
  for a in all_music_files_in_directory('/media/pi/LACIE/music/Storage3/whatcd/whatcd/Motorpsycho - Demon Box - 2014 4 CD (1993) [FLAC]'):
    print(a)
