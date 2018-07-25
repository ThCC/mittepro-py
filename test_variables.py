variables = {
    "recipients": [
        "Foo Bar <foo.bar@gmail.com>",
        "Fulano Aquino <fulano@gmail.com>",
        "<ciclano@gmail.com>"
    ],
    "context_per_recipient": {
        "foo.bar@gmail.com": {"foo": True},
        "fulano.arquino@gmail.com.br": {"bar": True}
    },
    "from_": 'Beutrano <beutrano@mail.com>',
    "from_2": '<beutrano@mail.com>',
    "template_slug": 'test-101',
    "message_text": "Using this message instead.",
    "message_html": "<em>Using this message <strong>instead</strong>.</em>",
    "key": '1e4be7cdd03545958e34',
    "secret": 'cf8cdba282104ed88f0a'
}
server_uri_test = 'http://0.0.0.0:8000'

search_variables = {
    'app_ids': '1001',
    'start': '2017-10-01',
    'end': '2017-10-31',
    'uuids': [
        '21da05e09a214bf',
        '7b9332128a3f461',
        '09f7ceac90fe4b3',
        '0f39a611031c4ff',
        'f2412b7062814de'
    ]
}
