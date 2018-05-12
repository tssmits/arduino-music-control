import csv

def get_item_for_qr_code(msg):
  with open('../map.csv', 'rb') as csvfile:
    mapreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in mapreader:
      if row[0] == msg:
        return {
          'key': row[0],
          'type': row[1],
          'uri': row[2]
        }

  return None

if __name__ == '__main__':
  print(get_item_for_qr_code('QR-Code:Hidden Orchestra - Archipelago'))
  print(get_item_for_qr_code('QR-Code:Pearl Jam - Ten'))
