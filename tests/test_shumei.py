import pytest

from wulu_shumei_bypass.shumei import Shumei
from wulu_shumei_bypass.trajectory import generate

mode = ['auto_slide', 'slide', 'spatial_select']
org = [
    'd6tpAY1oV0Kv5jRSgxQr',
    'xQsKB7v2qSFLFxnvmjdO',
    'eR46sBuqF0fdw7KWFLYa',
]


@pytest.mark.asyncio
@pytest.mark.parametrize('mode', mode)
@pytest.mark.parametrize('org', org)
async def test_shumei(mode, org):
    s = Shumei(organization=org, mode=mode)
    try:
        r = await s.register()
        result = await s.fverify(rr=r)
        print(result)
        assert result.get('riskLevel') == 'PASS', (
            f'Expected PASS, got {result.get("riskLevel")}'
        )
    except NotImplementedError as e:
        pytest.skip(reason=str(e))


@pytest.mark.asyncio
async def test_trajectory():
    for p in generate(72, duration=702):
        print(f'  [{p[0]:3d}, {p[1]:3d}, {p[2]:4d}],')
