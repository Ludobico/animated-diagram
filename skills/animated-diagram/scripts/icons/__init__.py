"""Icon registry for animated architecture diagrams.

One icon per module in this folder, registered automatically. A module defines
    KEY     name used in spec.json ("icon": KEY)
    SHAPE   what it looks like      } both feed references/icons.md
    MOTION  its micro-interaction   }
    draw(p, uid="", label="")  -> inline SVG
Drawing rules (core icons and --extra-icons files alike): local coordinates about +-26;
colours only from the group palette `p` (ink / hi / tint / line / acc, and `paper` for fills:
white in the light theme, a dark surface in the dark one; never hard-code #fff); at least one
micro-interaction whose period divides T (6, 3, 2, 1.5, 1.2, 1 s), phase offsets as a
negative `begin`; `uid` keeps clipPath ids unique when one icon is used by several nodes.
Modules whose name starts with "_" are helpers, not icons.
"""
import importlib
import importlib.util
import pkgutil
import re
import sys
from pathlib import Path

from icons._svg import T, anim, n, xform  # noqa: F401  (re-exported)

ICONS, INFO = {}, {}


def register(mod, origin):
    key = getattr(mod, "KEY", None)
    if not key or not callable(getattr(mod, "draw", None)):
        raise SystemExit(f"{origin}: an icon module needs KEY and draw(p, uid, label)")
    if key in ICONS:
        raise SystemExit(f"{origin}: icon {key!r} already exists; pick another KEY")
    ICONS[key] = mod.draw
    INFO[key] = (getattr(mod, "SHAPE", ""), getattr(mod, "MOTION", ""))


for _m in pkgutil.iter_modules(__path__):
    if not _m.name.startswith("_"):
        register(importlib.import_module(f"icons.{_m.name}"), _m.name)


def load_extra(path):
    """Register an icon drawn for one job (--extra-icons). Same format as a core module,
    so promoting it to the core library is a plain file copy into this folder."""
    path = Path(path)
    if not path.is_file():
        raise SystemExit(f"--extra-icons: no such file {path}")
    spec = importlib.util.spec_from_file_location(f"extra_icon_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    keep, sys.dont_write_bytecode = sys.dont_write_bytecode, True  # no __pycache__ in the user's folder
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = keep
    register(mod, str(path))
    return mod.KEY


# keyword -> icon, first match wins (English + Korean)
_RULES = [
    ("vector-db", r"vector|qdrant|pinecone|milvus|weaviate|chroma|faiss|pgvector|벡터"),
    ("database", r"postgres|mysql|maria|sql|database|\bdb\b|mongo|oracle|rds|dynamo|데이터베이스|디비"),
    ("cache", r"redis|memcache|cache|캐시"),
    ("queue", r"kafka|rabbit|queue|\bmq\b|sqs|pubsub|pub/sub|broker|nats|큐|메시지"),
    ("storage", r"\bs3\b|bucket|storage|blob|minio|\bnas\b|file|drive|스토리지|저장소|파일"),
    ("key", r"auth|oauth|oidc|\bsso\b|login|identity|credential|\btokens?\b|secret|vault|keycloak|okta|cognito|인증|로그인|토큰|자격"),
    ("shield-check", r"verif|validat|security|firewall|\bwaf\b|guard|검증|보안|방화벽"),
    ("terminal", r"claude code|\bcli\b|terminal|shell|console|ssh|터미널"),
    ("chip", r"embed|rerank|vllm|\bgpu\b|inference|triton|임베딩"),
    ("router", r"litellm|proxy|gateway|router|nginx|load.?balanc|ingress|게이트웨이|프록시|라우터"),
    ("trace", r"langfuse|trace|\blogs?\b|monitor|observab|metric|grafana|prometheus|sentry|otel|telemetry|모니터링|로그|추적"),
    ("plug", r"\bmcp\b|plugin|connector|adapter|커넥터"),
    ("chat-bot", r"slack|\bbot\b|chat|discord|teams|telegram|kakao|챗봇|봇"),
    ("llm", r"\bllm\b|gpt|claude|gemini|openai|anthropic|\bmodel\b|ollama|bedrock|모델"),
    ("poller", r"watch|poll|sync|cron|schedul|crawl|scrap|perforce|webhook|폴링|감시|동기화|스케줄"),
    ("service-graph", r"langgraph|agent|orchestrat|workflow|pipeline|에이전트|오케스트"),
    ("api", r"\bapi\b|rest|graphql|grpc|endpoint|sdk"),
    ("browser", r"\bweb\b|react|browser|front.?end|\bui\b|next\.?js|vue|dashboard|portal|웹|프론트|브라우저"),
    ("user", r"\buser|customer|human|actor|person|operator|사용자|유저|고객"),
    ("server", r"server|service|worker|backend|compute|ec2|lambda|function|\bjob\b|서버|서비스|워커|백엔드"),
    ("cloud", r"cloud|\baws\b|\bgcp\b|azure|\bcdn\b|saas|external|internet|클라우드|외부"),
]
_DATASTORES = {"vector-db", "database", "cache", "storage", "queue"}


def guess_icon(label, sub="", shape=None):
    """Pick an icon key from a node's label/sub-label (and Mermaid shape); None when no rule matches.

    There is deliberately no catch-all icon: a node nothing matches gets a core key chosen by hand
    or an icon drawn for it (references/custom-icons.md), never a placeholder.
    """
    text = f"{label} {sub or ''}".lower()
    guess = None
    for key, pat in _RULES:
        if re.search(pat, text):
            guess = key
            break
    if shape == "cylinder" and guess not in _DATASTORES:
        return "database"
    return guess
