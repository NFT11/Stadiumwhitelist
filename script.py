import json, pathlib, csv
from datetime import date, datetime
from decimal import Decimal

def main():

    name = 'public_presale'
    dt1 = datetime.strptime('2021-10-22T07:00:00+00:00','%Y-%m-%dT%H:%M:%S%z')
    dt2 = datetime.strptime('2021-12-11T10:01:00+00:00','%Y-%m-%dT%H:%M:%S%z')
    time_start = datetime.timestamp(dt1)
    time_cut = datetime.timestamp(dt2)
    min_amount = 88


    basepath = f"{pathlib.Path(__file__).parent.resolve()}"

    fromAddress = '0x4a63f4113eb45d8f25132757005a5be5bf4951c0'

    wallets = {}


    def file_multi():
        transactions = {}
        files = [
            f'{basepath}/export-token-0x73f67ae7f934ff15beabf55a28c2da1eeb9b56ec-202110.csv',
            f'{basepath}/export-token-0x73f67ae7f934ff15beabf55a28c2da1eeb9b56ec-202111.csv',
            f'{basepath}/export-token-0x73f67ae7f934ff15beabf55a28c2da1eeb9b56ec-202112.csv',
            ]
        for file in files:
            with open(file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if(row['Method']=='Buy' and row['From'] == fromAddress and ( time_start < int(row['UnixTimestamp']) < time_cut)):
                        if not row['Txhash'] in transactions:
                            transactions[row['Txhash']] = {'To':row['To'], 'Quantity': Decimal(row['Quantity'].replace(',','')) }

        for i, t in transactions.items():
            if t['To'] in wallets:
                wallets[t['To']] += t['Quantity']
            else:
                wallets[t['To']] = t['Quantity']

    file_multi()


    wallets = {k: v for k, v in sorted(wallets.copy().items(), key=lambda item: item[1])}


    for i, t in wallets.copy().items():
        wallets[i] = float(t)
    
    whitelist = {k: v for k, v in wallets.copy().items() if v >= min_amount}

    nonlist = {k: v for k, v in wallets.copy().items() if v < min_amount}



    file = f"{basepath}/{name}_all_{int(datetime.now().timestamp())}.json"

    with open(file, "w") as fp:
        json.dump(
            wallets,fp, indent=2)


    file = f"{basepath}/{name}_report_{int(datetime.now().timestamp())}.json"

    with open(file, "w") as fp:
        json.dump(
            {
                "info" : {
                    "min_amount" : min_amount,
                    "utc_time_start" : datetime.utcfromtimestamp(time_start).strftime('%Y-%m-%dT%H:%M:%S'),
                    "utc_time_cut" : datetime.utcfromtimestamp(time_cut).strftime('%Y-%m-%dT%H:%M:%S'),
                },
                "all" : {
                    "wallets_count": len(wallets.keys()), 
                    "wallets_amount": sum(list(wallets.values())),
                    "wallets": wallets,
                },
                "whitelist" : {
                    "wallets_count": len(whitelist.keys()),
                    "wallets_amount": sum(list(whitelist.values())),
                    "wallets": whitelist,
                },
                "nonlist" : {
                    "wallets_count": len(nonlist.keys()),
                    "wallets_amount": sum(list(nonlist.values())),
                    "wallets": nonlist,
                }
            },fp, indent=2)

    file = f"{basepath}/{name}_whitelist_{int(datetime.now().timestamp())}.json"
    with open(file, "w") as fp:
        json.dump(list(whitelist.keys()),fp, indent=2)


main()