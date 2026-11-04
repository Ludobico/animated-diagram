<h1 align="center">animated-diagram</h1>

<p align="center">
  구조도를 움직이는 GIF/SVG로 만드는 에이전트 스킬입니다.<br>
  노드마다 직접 그린 아이콘이 각자의 마이크로 인터랙션으로 움직이고, 연결선을 따라 데이터 패킷이 흐릅니다.
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/how-it-works-dark.gif">
    <img src="assets/how-it-works-light.gif" alt="animated-diagram 파이프라인(입력, 스펙, 렌더, 검사, 캡처)을 보여주는 움직이는 구조도" width="900">
  </picture>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/LICENSE-MIT-3fb950?style=for-the-badge&labelColor=4b4b4b"></a>
  <a href="pyproject.toml"><img alt="Python 3.10+" src="https://img.shields.io/badge/PYTHON-3.10%2B-3776ab?style=for-the-badge&labelColor=4b4b4b"></a>
  <a href="https://agentskills.io"><img alt="Agent Skills compatible" src="https://img.shields.io/badge/AGENT%20SKILLS-COMPATIBLE-8a2be2?style=for-the-badge&labelColor=4b4b4b"></a>
  <a href="README.md"><img alt="Language: English" src="https://img.shields.io/badge/LANG-ENGLISH-d9534f?style=for-the-badge&labelColor=4b4b4b"></a>
</p>

## 기능

- **세 가지 입력**: Mermaid 플로우차트, 텍스트 설명, 구조도 이미지(스크린샷, 사진, 화이트보드).
- **움직이는 아이콘**: 노드마다 각자의 동작을 가진 아이콘이 붙습니다. 맞는 아이콘이 없으면 에이전트가 같은 스타일로 그립니다.
- **흐르는 데이터 패킷**: 패킷이 데이터 방향을 따라 연결선 위를 이동합니다.
- **두 가지 선 표시 방식**: 처음부터 선이 보이거나, 선이 스스로 그려지고 6초마다 반복됩니다.
- **라이트/다크 테마**: 하나만 만들거나, 둘 다 만들어 README가 뷰어의 모드에 맞춰 바뀌게 할 수 있습니다.
- **전달 전 검사**: GIF를 캡처하기 전에 선 교차, 잘린 라벨, 노드 위를 지나는 선을 레이아웃 검사로 찾아냅니다.

## 동작 방식

위 애니메이션이 바로 이 파이프라인이며, 이 스킬이 [`assets/how-it-works.json`](assets/how-it-works.json)으로 그린 것입니다.

1. **스펙.** `mermaid_to_spec.py`가 Mermaid 플로우차트를 변환합니다. 텍스트나 이미지는 에이전트가 그룹(열), 노드,
   엣지로 된 `spec.json`을 직접 작성합니다.
2. **렌더.** `make_diagram.py`가 그룹을 열로 배치하고 노드마다 아이콘을 붙여, 6초마다 반복되는 움직이는
   SVG(SMIL)를 만듭니다.
3. **검사.** `check.py`는 잘린 라벨, 노드 위를 지나는 선, 자체 동작이 없는 아이콘을 실패로 처리합니다. 선
   교차는 경고만 합니다.
4. **캡처.** `capture.py`가 헤드리스 브라우저에서 SVG를 프레임 단위로 재생하고 Pillow로 GIF를 만듭니다.
   ffmpeg가 필요 없고 프레임이 빠지지 않습니다. 노드 6~11개 기준 0.7~1.3MB입니다.

스크립트는 [`skills/animated-diagram/scripts`](skills/animated-diagram/scripts)에 있습니다.

> [!NOTE]
> 구조를 그리는 도구이며, 메시지 순서나 단계별 상태 변화는 그리지 않습니다. 시퀀스 다이어그램은 참여자와
> 메시지를 플로우차트로 바꿔 다시 그립니다. 레이아웃 한계와 검증 범위는
> [`references/limits.md`](skills/animated-diagram/references/limits.md)에 있습니다.

## 설치

코딩 에이전트(Claude Code, Codex, Cursor 등 [Agent Skills](https://agentskills.io)를 지원하는 에이전트)에
아래 문장을 붙여 넣으세요.

```text
Read https://raw.githubusercontent.com/Ludobico/animated-diagram/main/INSTALL.md and follow it to install the animated-diagram skill.
```

에이전트가 저장소를 내려받고, 스킬 폴더에 연결한 뒤, 동작 확인까지 합니다. [INSTALL.md](INSTALL.md)는
일반 마크다운이라 무엇을 할지 미리 읽어 볼 수 있습니다.

<details>
<summary>직접 설치 (Claude Code, Codex)</summary>

먼저 한 번 내려받습니다.

```bash
git clone --depth 1 https://github.com/Ludobico/animated-diagram.git ~/.animated-diagram
```

**Claude Code**

```bash
ln -s ~/.animated-diagram/skills/animated-diagram ~/.claude/skills/animated-diagram
```

Windows(PowerShell):

```powershell
New-Item -ItemType Junction -Path "$HOME\.claude\skills\animated-diagram" -Target "$HOME\.animated-diagram\skills\animated-diagram"
```

**Codex**

```bash
mkdir -p ~/.codex/skills
ln -s ~/.animated-diagram/skills/animated-diagram ~/.codex/skills/animated-diagram
```

Windows(PowerShell):

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
New-Item -ItemType Junction -Path "$HOME\.codex\skills\animated-diagram" -Target "$HOME\.animated-diagram\skills\animated-diagram"
```

한 프로젝트에서만 쓰려면 대신 `<프로젝트>/.agents/skills/`에 연결하세요. Codex는 새 스킬을 자동으로 인식하며,
보이지 않으면 Codex를 다시 시작한 뒤 `$`를 입력하거나 `/skills`를 실행해 찾으세요.

업데이트는 `git -C ~/.animated-diagram pull`입니다.

> [!NOTE]
> Codex 설치 절차는 Windows의 Codex CLI 0.165.0에서 확인했습니다. 스킬이 발견되고, 이름과 설명을 읽고,
> junction을 따라가는 것까지입니다. Codex 모델로 끝까지 실행해 본 것은 아닙니다.

</details>

<details>
<summary>Claude Desktop / claude.ai</summary>

같은 문장을 주면 ZIP을 만들어 줍니다. 그 ZIP을 Customize → Skills에서 업로드하세요.

</details>

> [!NOTE]
> Claude Desktop과 claude.ai에서는 스크립트가 Anthropic 클라우드 샌드박스에서 실행되므로 GIF 없이 움직이는
> SVG만 나올 수 있습니다.

## 사용

에이전트에게 이렇게 요청하세요.

- "이 Mermaid 구조도를 움직이는 GIF로 만들어 줘"
- "이 아키텍처 스크린샷을 다크 테마로 움직이게 해 줘"
- "웹 앱, API 게이트웨이, Redis, Postgres로 된 구조야. 움직이는 구조도로 만들어 줘"

에이전트가 선이 스스로 그려지게 할지, 어떤 테마를 쓸지 한 번 물은 뒤, 스펙 작성, 렌더링, 검사, 캡처까지
진행합니다. 예제는 [`skills/animated-diagram/examples`](skills/animated-diagram/examples)에 있습니다.

### 옵션

| 선택 | 값              | 효과                                                                 |
| ---- | --------------- | -------------------------------------------------------------------- |
| 선   | `static`        | 선, 화살표, 라벨이 첫 프레임부터 보입니다. 패킷만 움직입니다.        |
|      | `draw`          | 선이 그려지고 패킷이 흐른 뒤, 선이 사라지며 반복됩니다.              |
| 테마 | `light`, `dark` | `dark`는 GitHub 다크 배경을 써서 README에 자연스럽게 섞입니다.       |
|      | 둘 다           | 둘 다 만들어 README가 뷰어의 모드에 맞춰 바뀌게 합니다(아래 스니펫). |

뷰어의 모드에 맞춰 바꾸려면 GIF 두 개를 이렇게 넣으세요.

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="diagram-dark.gif" />
  <img src="diagram-light.gif" alt="architecture diagram" />
</picture>
```

글자를 더 선명하게 하려면 대신 움직이는 SVG를 `<img src="diagram.svg">`로 넣으세요. 채팅 앱, 이메일, 슬라이드는
SVG의 첫 프레임만 보여 주는 경우가 많으니 GIF도 함께 두세요. `GIF_WIDTH`로 GIF 크기를, `GIF_COLORS`로 팔레트
크기를 바꿀 수 있습니다.

### 아이콘

노드마다 내장 아이콘 중 하나가 라벨에서 골라져 붙습니다(`redis`는 캐시 아이콘, `kafka`는 큐 아이콘 등). 다른
아이콘을 쓰려면 노드에 `"icon"`을 지정하세요. 맞는 게 없으면 에이전트가 같은 스타일로 새 아이콘을 그리며, 그
작업에서만 쓰입니다. 전체 목록은 [`references/icons.md`](skills/animated-diagram/references/icons.md)에 있습니다.

## 예제

### Mermaid로 만들기

> `examples/mermaid-architecture.mmd`를 움직이는 GIF로 만들어 줘

([`mermaid-architecture.mmd`](skills/animated-diagram/examples/mermaid-architecture.mmd)).

<details>
<summary>Mermaid 입력</summary>

```text
flowchart LR
    subgraph Client
        UI["web/app.py<br/>UI"]
    end
    subgraph API
        MAIN["main.py<br/>API"]
        RD[("Redis<br/>memory")]
    end
    subgraph Graphs
        SG[serving_graph]
        LG["learning_graph<br/>evaluator → reflector → curator"]
    end
    subgraph Playbook
        ST[("Qdrant + SQL<br/>playbook")]
    end
    UI -->|POST /chat/stream| MAIN
    MAIN -->|SSE data| UI
    MAIN -->|save_user_message / save_ai_message| RD
    MAIN -->|solution_stream| SG
    SG -->|token 스트림| MAIN
    SG -->|bullet 검색| ST
    MAIN -.->|run_background_learning| LG
    LG -->|update_playbook_node| ST
```

</details>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/example-mermaid-dark.gif">
    <img src="assets/example-mermaid-light.gif" alt="챗 서비스의 클라이언트, API, 그래프, 플레이북을 보여주는 움직이는 구조도" width="900">
  </picture>
</p>

### 설명으로 만들기

> CPU 프로세서에서 ALU, 레지스터, L1~L3 캐시의 구조도를 그려주고, 이게 DRAM과 버스로 통신하는 다이어그램을
> 그려줘. 라인은 처음에 없다가 이어지는 형태로, light 테마로 그려줘

이 요청은 선 표시 방식과 테마를 이미 말하고 있어서 에이전트가 이를 묻지 않습니다. 요청에 없는 부분만
물어보는데, 여기서는 CPU 안의 화살표 방향이었습니다. CPU 안은 요청 경로를 따라 바깥쪽으로 향하고, 버스 구간은
양방향입니다.

<p align="center">
  <img src="assets/example-cpu-ko.gif" alt="ALU, 레지스터, L1~L3 캐시를 가진 CPU가 메모리 버스로 DRAM과 연결된 움직이는 구조도" width="900">
</p>

### 이미지로 만들기

> (그림을 첨부하고) 이 구조도를 움직이는 GIF로 만들어 줘. light 테마로, 선은 처음부터 이어진 형태로 해 줘

입력은 [Attention Is All You Need](https://arxiv.org/abs/1706.03762)(Vaswani 외, 2017)의 Figure 1이었습니다.
원본 그림은 이 저장소에 포함하지 않았습니다. 스킬은 그 구조를 새로 그리며, 렌더링 전에 그림에서 읽어 낸 것과
뺀 것을 목록으로 보여 줍니다. 여기서는 Add & Norm 노드가 잔차 연결을 대신하므로 잔차 선은 뺐습니다.

<p align="center">
  <img src="assets/example-transformer-ko.gif" alt="인코더, 디코더, 임베딩, 어텐션, 피드 포워드, 선형 층, 소프트맥스로 이루어진 트랜스포머 구조의 움직이는 구조도" width="900">
</p>

## 요구 사항

- Python 3.10 이상
- GIF 캡처: Pillow와 Playwright(`uv run`이 둘 다 설치하거나 `pip install pillow playwright`), 그리고 Chrome,
  Edge 또는 `playwright install chromium`

브라우저가 없어도 브라우저와 README에서 재생되는 움직이는 SVG는 만들 수 있습니다.
