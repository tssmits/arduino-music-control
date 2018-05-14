import csv

def get_item_for_qr_code(msg, csv_filename='map.csv'):
  with open(csv_filename, 'r') as csvfile:
    mapreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in mapreader:
      print(msg)
      if row[0] == msg:
        return {
          'key': row[0],
          'type': row[1],
          'uri': row[2]
        }

  return None

if __name__ == '__main__':
  print(get_item_for_qr_code('QR-Code:HiddenOrchestra-Archipelago'))
  print(get_item_for_qr_code('QR-Code:Pearl Jam - Ten'))
  print(get_item_for_qr_code('QR-Code:nonexistant'))
