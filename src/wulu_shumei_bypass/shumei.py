import json
import random
import time
from typing import Any

from typing_extensions import Unpack
from wreq import Client

from wulu_shumei_bypass._type import Mode, RegisterResult, ShumeiParams, VerifyResult
from wulu_shumei_bypass.slover import (
    solve_icon,
    solve_select,
    solve_seq_select,
    solve_slide,
    solve_spatial_select,
)
from wulu_shumei_bypass.trajectory import generate, times

from ._type import SolverMapping
from .config import CryptoConfig
from .sign import encrypt_field as _encrypt

_JSON = lambda v: json.dumps(v, separators=(',', ':'))
_parse_jsonp = lambda t: (
    json.loads(t.strip()[t.strip().index('(') + 1 : -1])
    if t.strip().endswith(')')
    else json.loads(t.strip())
)
get_time = lambda: int(time.time() * 1000)


class Shumei:
    BASE_URL = 'https://captcha.fengkongcloud.com'
    STATIC_URL = 'https://castatic.fengkongcloud.cn'

    _solver: SolverMapping = {
        'slide': solve_slide,
        'spatial_select': solve_spatial_select,
        'icon_select': solve_icon,
        'auto_slide': lambda _=None: 1,  # auto_slide doesn't need to solve
        'seq_select': solve_seq_select,
        'select': solve_select,  # NotImplemented
    }

    def __init__(self, **kwargs: Unpack[ShumeiParams]):
        self.organization = kwargs['organization']
        self.app_id = kwargs.get('app_id', 'default')
        self.channel = kwargs.get('channel', 'default')
        self.version = kwargs.get('version', '1.0.4')
        self.sdkver = kwargs.get('sdkver', '1.1.3')
        self.mode: Mode = kwargs.get('mode', 'slide')
        self.lang = kwargs.get('lang', 'zh-cn')
        self.os_type = kwargs.get('os_type', 'web_pc')
        self.captcha_uuid = kwargs.get('captcha_uuid', self._uuid())
        self.safe_params = '1' + ('0' if kwargs.pop('xhr_hooked', True) else '1')
        self.custom_data = kwargs.get('custom_data', {})
        self.os_type = (self.custom_data.get('os', self.os_type)).lower()
        self._http = Client()

    async def _get(self, path: str, params: dict[str, str]) -> Any:
        params['callback'] = f'sm_{int(time.time() * 1000)}'
        resp = await self._http.get(f'{Shumei.BASE_URL}{path}', query=params)
        return _parse_jsonp(await resp.text())

    def encrypt(self, visual_name: str, value) -> dict[str, str]:
        fn, fk = getattr(CryptoConfig, visual_name)
        data = value.encode() if isinstance(value, str) else _JSON(value).encode()
        return {fn: _encrypt(fk, data)}

    # ── register ──────────────────────────────────────────────────────────

    def _uuid(self) -> str:
        ts = time.strftime('%Y%m%d%H%M%S')
        cs = ''.join(
            random.choices('ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678', k=18)
        )
        return ts + cs

    async def register(self) -> RegisterResult:
        params: dict[str, str] = {
            'organization': self.organization,
            'appId': self.app_id,
            'channel': self.channel,
            'lang': self.lang,
            'model': self.mode,
            'rversion': self.version,
            'captchaUuid': self.captcha_uuid,
            'sdkver': self.sdkver,
            'data': _JSON(self.custom_data or {}),
        }
        resp = await self._get('/ca/v1/register', params)
        if isinstance(resp, dict) and resp.get('code') == 1100:
            return resp.get('detail')  # type: ignore

        raise Exception(f'Register failed: {resp}')

    async def fetch_img(self, path: str):
        return await (await self._http.get(f'{self.STATIC_URL}{path}')).bytes()

    async def fverify(self, rr: RegisterResult, *, true_width=300) -> VerifyResult:
        et = now = get_time()
        if self.mode in ('select', 'icon_select', 'seq_select'):
            st = now - random.randint(3000, 8000)  # 点选需要读题时间
        else:
            st = now - random.randint(1000, 1800)
        enc = self.encrypt
        true_height = true_width // 2

        body = {
            'organization': self.organization,
            'rid': rr['rid'],
            'captchaUuid': self.captcha_uuid,
            'rversion': self.version,
            'sdkver': self.sdkver,
            'protocol': CryptoConfig.protocol,
            'ostype': 'web',
            'act.os': self.os_type,
            **enc('appId', self.app_id),
            **enc('channel', self.channel),
            **enc('lang', self.lang),
            **enc('safeParams', self.safe_params),
            **enc('duration', et - st),
            **enc('trueWidth', true_width),
            **enc('trueHeight', true_height),
            # 😅 Maybe it's a bug? always 1
            **enc('consoleCheck', 1),
            **enc('botDetection', 0),
            **enc('fixed', -1),
        }

        if self.mode not in self._solver:
            raise NotImplementedError(f'unsupported mode: {self.mode}')

        bg = await self.fetch_img(rr['bg']) if rr.get('bg') else None
        fp = await self.fetch_img(rr['fg']) if rr.get('fg') else None

        if self.mode == 'slide':
            x = self._solver[self.mode](bg, fp)  # type: ignore
            body |= enc('slideRatio', x)
            data = generate(int(x * true_width), 0, et - st)
            body |= enc('mouseData', data)
        elif self.mode == 'auto_slide':
            body |= enc('slideRatio', 1)
            data = generate(int(true_width * 0.867), 0, et - st)
            body |= enc('mouseData', data)
        elif self.mode == 'spatial_select':
            order = rr['order']  # type: ignore
            point = self._solver[self.mode](bg, order[0])  # type: ignore
            data = [[*point, get_time()]]
            body |= enc('selectData', data)
            body |= enc('mouseData', data)
        elif self.mode == 'select':
            pos = self._solver[self.mode](bg, rr['order'])  # type: ignore
        elif self.mode == 'icon_select':
            pos = self._solver[self.mode](bg, fp)  # type: ignore
        elif self.mode == 'seq_select':
            pos = self._solver[self.mode](bg)  # type: ignore
        else:
            raise NotImplementedError(f'unsupported mode: {self.mode}')

        if self.mode in ('select', 'icon_select', 'seq_select'):
            ts = times(st, et, len(pos))
            data = [[*p, t] for p, t in zip(pos, ts)]
            body |= enc('selectData', data)
            body |= enc('mouseData', data)
            body |= enc('duration', ts[-1] - st)

        return await self._get('/ca/v2/fverify', body)

    async def solve(self, retry: int = 3) -> VerifyResult:
        for _ in range(retry):
            reg = await self.register()
            verify_res = await self.fverify(rr=reg)
            if verify_res['code'] != 1100:
                raise Exception(f'Verify failed: {verify_res}')
            if verify_res.get('riskLevel') == 'PASS':
                return verify_res

        raise Exception(f'All attempts failed: last verify result: {verify_res}')

    @classmethod
    def add_solver(cls, mode: Mode):
        def decorator(func):
            cls._solver[mode] = func  # type: ignore
            return func

        return decorator
