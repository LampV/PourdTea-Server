import json
import requests
PAGE_SIZE = 10
TOP_SIZE = 50


def get_require_str(require_fields, rename_dict):
    require_fields_str = ''
    for field in require_fields:
        if field not in rename_dict:
            require_fields_str += field
        else:
            origin_name, cur_name = rename_dict[field], field
            require_fields_str += '{} as {}'.format(origin_name, cur_name)
        require_fields_str += ', '
    require_fields_str = require_fields_str[:-2]
    return require_fields_str


def code2session(jscode):
    """
    通过qq小程序给出的jscode，换取session信息
    :param jscode:  jscode
    :return: openid, session_ksy
    """
    appid = 'wx5f287c54e4faa297'
    secret = '857e800532eb810daad0470d85c6d9b9'
    request_url = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'.format(
        appid, secret, jscode
    )
    res = requests.get(request_url)
    qq_data = json.loads(res.content.decode())
    openid, session_key = qq_data['openid'], qq_data['session_key']
    return openid, session_key
