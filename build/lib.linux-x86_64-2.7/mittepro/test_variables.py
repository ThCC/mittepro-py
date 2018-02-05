variables = {
    "recipients": [
        "Thiago de Castro <thiago.decastro2@gmail.com>",
        # "Thiago C de Castro <THIAGO.CIRRUS@ALTERDATA.COM.BR>",
        # "<success@simulator.amazonses.com>",
        # "<bounce@simulator.amazonses.com>",
        # "<ooto@simulator.amazonses.com>",
        # "<complaint@simulator.amazonses.com>",
        # "<suppressionlist@simulator.amazonses.com>",
    ],
    "context_per_recipient": {
        "thiago.decastro2@gmail.com": {"foo": True},
        "thiago.cirrus@alterdata.com.br": {"bar": True}
    },
    "from_name": 'MittePro',
    "from_email": 'mittepro@alterdata.com.br',
    "template_slug": 'test-101',
    "message_text": "Using this message instead.",
    "message_html": "<em>Using this message <strong>instead</strong>.</em>",
    "key": '1e4be7cdd03545958e34',
    "secret": 'cf8cdba282104ed88f0a'
}
server_uri_test = 'http://172.16.72.2:8001'
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
