variables = {
    "recipients": [
        "Thiago de Castro <thiago.decastro2@gmail.com>",
        "Thiago C de Castro <THIAGO.DSN.cir@ALTERDATA.COM.BR>",
        # "<success@simulator.amazonses.com>",
        # "<bounce@simulator.amazonses.com>",
        # "<ooto@simulator.amazonses.com>",
        # "<complaint@simulator.amazonses.com>",
        # "<suppressionlist@simulator.amazonses.com>",
    ],
    "context_per_recipient": {
        "thiago.decastro2@gmail.com": {"foo": True},
        # "thiago.dsn.cir@alterdata.com.br": {"bar": True}
    },
    'batchs': 2,
    'time_between_batchs': 5,
    "from_": 'MittePro <mittepro@alterdata.com.br>',
    "from_2": '<mittepro@alterdata.com.br>',
    "template_slug": 'teste-01',
    "message_text": "Using this message instead.",
    "message_html": "<em>Using this message <strong>instead</strong>.</em>",
    "key": '1e4be7cdd03545958e34',
    "secret": 'cf8cdba282104ed88f0a',
    "files_names": [
        # 'pdf-121_KB.pdf',
        # 'jpg-0_9_MB.jpg',
        # 'IMG_0563.JPG',
        # 'localcao_asscon.pdf',
        # '2_7_mb.jpg',
        # '2_7_mb.jpg',
        # '2_mb.jpg',
        # '2_mb.jpg',
        # '1_1_mb.jpg',
        '1_1_mb.jpg',
        # 'foo.txt',
    ]
}
server_uri_test = 'http://0.0.0.0:8000'
search_variables = {
    'app_ids': '1001',
    'start': '2017-02-27',
    'end': '2017-09-26',
    'uuids': [
        '21da05e09a214bf',
        '7b9332128a3f461',
        '09f7ceac90fe4b3',
        '0f39a611031c4ff',
        'f2412b7062814de'
    ]
}
