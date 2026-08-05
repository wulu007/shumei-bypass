from typing import (
    Any,
    Callable,
    Literal,
    NotRequired,
    Required,
    TypedDict,
)

RiskLevel = Literal['PASS', 'REJECT', 'REVIEW']


class VerifyResult(TypedDict, total=False):
    code: Required[int]
    riskLevel: RiskLevel
    requestId: str
    message: str


class RegisterResult(TypedDict):
    rid: str
    k: str
    l: int
    fg: str
    bg: str
    bg_height: NotRequired[int]
    bg_width: NotRequired[int]
    domains: NotRequired[list[str]]
    order: NotRequired[list[str]]


Mode = Literal[
    'auto_slide',
    'slide',
    'select',
    'icon_select',
    'seq_select',
    'spatial_select',
]

OSType = Literal['web_pc', 'web_mobile']


class ShumeiParams(TypedDict, total=False):
    organization: Required[str]
    app_id: str
    channel: str
    version: str
    sdkver: str
    mode: Mode
    lang: str
    os_type: OSType
    captcha_uuid: str
    xhr_hooked: bool
    custom_data: dict[str, Any]


class SolverMapping(TypedDict, total=False):
    auto_slide: Callable[[Any], Any]
    slide: Callable[[bytes, bytes], float]
    select: Callable[[bytes, list[str]], list[list[float]]]
    icon_select: Callable[[bytes, bytes], list[list[float]]]
    seq_select: Callable[[bytes], list[list[float]]]
    spatial_select: Callable[[bytes, str], tuple[float, float]]


class InvalidOrganizationError(Exception):
    pass
