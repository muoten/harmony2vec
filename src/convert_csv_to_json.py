import os
from utils.parse_config import config


import pandas as pd
import json

# read from vectors and metadata and create a json file with the following format:

# example = {"rows":[{"primary_key":-108,"vector":[0.275379527583933,0.2158638218686412,0.1855042597225507,0.1524307406462238,0.2073455563090693,0.170938615281085,0.2257252011188041,0.2860373583986773,0.1799759329418784,0.202549392607184,0.2829011352559943,0.244610223094115,0.2969066343578783,0.1645848183463549,0.2153665932216983,0.2358163291747093,0.1862892195330987,0.1706676435598976,0.1795881054110504,0.2972186130134231],"title":"r2aoz6yl0i_randomVarChar","duration":1.00192,"chord_set":"8dkvs5nrogk_randomVarChar"},{"primary_key":-122,"vector":[0.1836952673646263,0.1614749622400064,0.236636991829572,0.2154097784347855,0.2110401535891239,0.1672694728127779,0.2075816487840202,0.1992278331086725,0.1568289500393212,0.2911091575026096,0.2512282561482358,0.1705876230133343,0.2388860529281794,0.2101545398546974,0.1865412378136603,0.3066621762295288,0.2754705743380813,0.2914048623468066,0.2412612415424367,0.1784665234990084],"title":"6xayblw4fhk_randomVarChar","duration":7.67957,"chord_set":"985j8wtrbt_randomVarChar"},{"primary_key":-65,"vector":[0.2234173798081693,0.2569119996455631,0.2134023485797576,0.1848141715545541,0.2793627600360278,0.2550785131442689,0.2783952710979806,0.1753721059874415,0.2060471018273654,0.1746444128271976,0.1935692065582035,0.1999246014066345,0.1905071229194951,0.2066156325771493,0.2245112943963449,0.1819837235175093,0.2424526531050359,0.1725530033304211,0.2936154065111768,0.2556305496996051],"title":"ad3kz26f8a_randomVarChar","duration":1.29737,"chord_set":"4pkb4s0lad_randomVarChar"},{"primary_key":-118,"vector":[0.2962158543914969,0.2331045195866248,0.1919638373859957,0.2001170915126488,0.242270441917404,0.2200529607697435,0.2636681767617363,0.1876619755153734,0.2941852875720617,0.1834761672129454,0.1865853410122657,0.1782315466480816,0.1708913123634361,0.2447793726121121,0.2716218428641449,0.186501405995542,0.1601150509920268,0.2227374462058428,0.2859060791703796,0.166442662181863],"title":"8fr3snaqig_randomVarChar","duration":4.62645,"chord_set":"iqu1s9x4pkl_randomVarChar"},{"primary_key":73,"vector":[0.2058851640739932,0.1804870278731518,0.2482862347968832,0.2769109413488791,0.1654873437761361,0.1590953951311913,0.195186644731467,0.2281920406527413,0.2441591367244878,0.2764139218864463,0.2533019826690648,0.1768786421367089,0.2752654194888095,0.1559116117659194,0.2208362712383359,0.1841471455125371,0.2372296168144996,0.2657318727338189,0.2312863352013031,0.2218870887446922],"title":"8yomvz3q7d_randomVarChar","duration":7.0637,"chord_set":"8dyaxeh2y3_randomVarChar"},{"primary_key":12,"vector":[0.1696991536206049,0.226378250572663,0.208338641785301,0.2355401106568709,0.2082606824118782,0.2342982438126957,0.2433890832997497,0.2213954292535388,0.2277826720277434,0.2519978362997495,0.2151466371602769,0.2673651078561279,0.1685342110773694,0.2300135240246407,0.211469921839376,0.1445657576477344,0.2072968924857732,0.2015744594297867,0.2723068946729381,0.2769557044849115],"title":"4ize9oqttdg_randomVarChar","duration":5.91061,"chord_set":"n7qgu4bf2c_randomVarChar"},{"primary_key":-61,"vector":[0.2638669857847293,0.2764128285023082,0.2047610131635299,0.2731686405706455,0.2806902084365556,0.2278607101813072,0.1609156532619223,0.2276884699347853,0.2023495992468297,0.2060521822387444,0.2340060975683934,0.1463056622891526,0.1801863494247553,0.1408814576470575,0.2106082178045519,0.2806829436875811,0.2530614152184383,0.2539046138001229,0.195319913533335,0.1652289146406685],"title":"2cx9t69ulrg_randomVarChar","duration":8.68126,"chord_set":"8cm36t5gho_randomVarChar"},{"primary_key":67,"vector":[0.2498255103575123,0.2122154345829362,0.1716151718707344,0.1874211180438019,0.2225550389023702,0.2490052134707715,0.1466613050033556,0.2013238020700735,0.2415322103444962,0.2750378385571874,0.1620416328594803,0.2716126566519119,0.1454575219099573,0.2685382789538197,0.1816251096233538,0.2523000676846282,0.2150864684145685,0.2004725264475245,0.2614999978058276,0.2750205559526633],"title":"6nplt773a_randomVarChar","duration":6.64344,"chord_set":"oadjqsbfs5_randomVarChar"},{"primary_key":-43,"vector":[0.2243204272799121,0.1991033622139667,0.1823491134069505,0.2739822985197001,0.2125414491606326,0.2356055591477902,0.1986592727055318,0.2254674530987151,0.1859119754734294,0.2077941621107151,0.1816728905267234,0.2772149929271145,0.2164608614164776,0.2808825637795664,0.2947939802389089,0.1837876364136246,0.1566536165867038,0.2430353076139391,0.1584049837888478,0.2607883116411125],"title":"mfggqqz171_randomVarChar","duration":6.30987,"chord_set":"6kylepkqg6_randomVarChar"},{"primary_key":53,"vector":[0.1892973401450783,0.237612639767076,0.2877445036026142,0.2123156077439254,0.2510698765108915,0.170574694893442,0.2133081259066631,0.2358399766091825,0.2427741932158136,0.2479633001472434,0.258865537258017,0.1535385808573811,0.2776053527409829,0.2734642349098344,0.1674444026575295,0.1774452653653504,0.2472144090935892,0.1516889770006699,0.2389833151214936,0.151523263474588],"title":"39l0s7j3n6_randomVarChar","duration":2.88122,"chord_set":"55uzourugv_randomVarChar"}]}

def convert_csv_to_json():
    # Read the CSV files
    vectors_df = pd.read_csv(config['VECTOR_OUTPUT_FILE'], header=None, sep='\t')
    metadata_df = pd.read_csv(config['METADATA_OUTPUT_FILE'], sep='\t')

    # there is no primary key in the vectors_df, so we need to use the index
    merged_df = pd.merge(vectors_df, metadata_df, how='inner', left_index=True, right_index=True)

    # Create the JSON structure
    json_data = {
        "rows": []
    }
    print(merged_df.columns)

    # Iterate through the merged dataframe and create the JSON structure
    # for the vector field we need to use columns 0 to 19
    # for the chord_set field we need to use the column "chord_set" and convert it to a string
    for index, row in merged_df.iterrows():
        json_data["rows"].append({
            "primary_key": index,
            "vector": row[0:20].tolist(),
            "title": row["title"],
            "duration": row["duration"],
            "chord_set": row["chords_set"]
        })

    # Write the JSON data to a file
    with open(config['DATA_MILVUS_OUTPUT_FILE'], 'w') as f:
        json.dump(json_data, f)

    print("JSON file has been created successfully.")
