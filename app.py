import random
import time
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="2026 YUnicorn - 가챠 토너먼트 서바이벌",
    page_icon="🃏",
    layout="centered",
)

# ----------------------------------------------------
# [실시간 60인 동시 접속 멀티플레이어 데이터베이스]
# ----------------------------------------------------
@st.cache_resource
def get_shared_gacha_state():
    return {
        "players": {},  # {이름: {"card": 카드정보, "power": 전투력}}
        "tournament_tree": [],  # 대진표
        "match_results": [],  # 매치 결과
        "current_round_name": "",  # 라운드 이름
        "is_game_started": False,
        "is_simulating": False,  # 애니메이션 진행 중 여부
        "simulation_step": 0,    # 사다리 애니메이션 단계
        "champion": "",  # 최종 우승자
        "last_update": time.time(),  # 전역 최신화 타임스탬프
    }


game_state = get_shared_gacha_state()

# ----------------------------------------------------
# [알록달록 대규모 가챠 능력치 카드 DB (총 50종)]
# ----------------------------------------------------
GACHA_CARDS = [
    # 1. SSR 등급 - 초우량 창업가 & 전설의 능력자 (10종)
    {"rank": "SSR", "title": "🌟 스티브 잡스급 피칭 마법사", "power": 98, "desc": "발표 한 번에 심사위원 눈물 찔끔!"},
    {"rank": "SSR", "title": "⭐ 100억 투자 유치 대박 창업가", "power": 96, "desc": "통장 잔고가 멈추지 않는 수퍼 벤처!"},
    {"rank": "SSR", "title": "✨ 혼자서 다 하는 올라운더 천재", "power": 95, "desc": "코딩, 디자인, 기획 혼자서 뚝딱!"},
    {"rank": "SSR", "title": "👑 빌 게이츠급 파트너십 마스터", "power": 94, "desc": "전 세계 글로벌 기업과 순식간에 계약 완료!"},
    {"rank": "SSR", "title": "🚀 일론 머스크급 우주급 추진력", "power": 93, "desc": "남들이 안 된다고 할 때 이미 화성 가 있는 사람!"},
    {"rank": "SSR", "title": "🔥 밤샘 3일 연속 멀쩡한 무한 체력", "power": 92, "desc": "박카스 없이 피칭 데이까지 팔팔함 유지!"},
    {"rank": "SSR", "title": "💎 유니콘 기업 3개 연쇄 창업가", "power": 91, "desc": "손대는 아이템마다 대박 행진!"},
    {"rank": "SSR", "title": "🤖 인간을 뛰어넘은 AI 자체 탑재자", "power": 90, "desc": "생각하는 즉시 사업계획서 자동 생성!"},
    {"rank": "SSR", "title": "🦄 심사위원 마인드 컨트롤 능통자", "power": 89, "desc": "어떤 까다로운 질문도 1초 만에 감동으로 승화!"},
    {"rank": "SSR", "title": "⚡ 전 세계 유저 1,000만 명 보유자", "power": 88, "desc": "출시하자마자 App Store 1위 등극!"},

    # 2. SR 등급 - 핵심 멘토 & 엘리트 창업 인재 (15종)
    {"rank": "SR", "title": "🦄 아이디어 퐁퐁 아이디어 뱅크", "power": 87, "desc": "막힐 때마다 신박한 아이디어 샘솟음!"},
    {"rank": "SR", "title": "🔮 밤샘 피칭 무한 체력왕", "power": 86, "desc": "새벽 5시에도 에너지 200% 완충!"},
    {"rank": "SR", "title": "💜 심사위원 취향저격 사이다", "power": 85, "desc": "송곳 질문 들어와도 당당하게 완파!"},
    {"rank": "SR", "title": "👑 우리 팀 핵심 기둥 멘탈왕", "power": 84, "desc": "어떤 위기 상황도 웃으면서 해결!"},
    {"rank": "SR", "title": "📊 3초 컷 데이터 시장 분석가", "power": 83, "desc": "빅데이터로 소비자의 마음을 정확히 타격!"},
    {"rank": "SR", "title": "🎨 예술의 경지 UI/UX 디자이너", "power": 82, "desc": "누르면 바로 사고 싶어지는 환상의 디자인!"},
    {"rank": "SR", "title": "🎯 소름 돋는 타겟 마케팅 천재", "power": 81, "desc": "광고비 1원으로 100만 명 끌어모으기!"},
    {"rank": "SR", "title": "☕ 멘토님 사랑받는 애교쟁이", "power": 80, "desc": "질문 한 번에 멘토님의 극찬 쏟아짐!"},
    {"rank": "SR", "title": "🛡️ 어떠한 공격도 막는 Q&A 방어막", "power": 79, "desc": "예상 질문 리스트 100개 완벽 대비!"},
    {"rank": "SR", "title": "🤝 황금 인맥 네트워킹 귀재", "power": 78, "desc": "처음 본 사람과 5분 만에 형 동생 맺기!"},
    {"rank": "SR", "title": "📣 청중을 압도하는 보이스 보유자", "power": 77, "desc": "목소리 하나로 마이크 없이 회장 압도!"},
    {"rank": "SR", "title": "💡 10분 만에 BMC 사업계획서 완성", "power": 76, "desc": "핵심만 쏙쏙 뽑아내는 일처리 능력자!"},
    {"rank": "SR", "title": "🏆 특성화고 최고의 기술 보유자", "power": 75, "desc": "손만 대면 기계가 고쳐지는 장인의 손길!"},
    {"rank": "SR", "title": "🌈 팀원 전체 사기 충천 유포자", "power": 74, "desc": "지친 팀원들에게 긍정 에너지 무한 주입!"},
    {"rank": "SR", "title": "🎬 1분 쇼츠 홍보 영상 제작 달인", "power": 73, "desc": "조회수 100만 회 바이럴 영상 제조기!"},

    # 3. R 등급 - 실전 루키 & 듬직한 실무자 (15종)
    {"rank": "R", "title": "🍃 3초 컷 PPT 디자인 요정", "power": 72, "desc": "템플릿 하나는 예술 작품으로 승화!"},
    {"rank": "R", "title": "🍀 엑셀&데이터 계산기 마스터", "power": 71, "desc": "시장 조사와 수치 계산 완벽 정리!"},
    {"rank": "R", "title": "☕ 멘토님 커피 셔틀 센스쟁이", "power": 70, "desc": "칭찬과 사랑을 한 몸에 받는 능구렁이!"},
    {"rank": "R", "title": "🌱 오뚝이 기업가정신 루키", "power": 69, "desc": "실패해도 해맑게 다시 일어서는 잡초!"},
    {"rank": "R", "title": "📝 초스피드 회의록 작성자", "power": 68, "desc": "말하는 족족 다 타이핑해버리는 타자왕!"},
    {"rank": "R", "title": "⏰ 칼 같은 데드라인 준수자", "power": 67, "desc": "약속된 시간 1분 전에 완벽 제출!"},
    {"rank": "R", "title": "🍕 야식 메뉴 배달 1등 신속 배송", "power": 66, "desc": "배달 라이더보다 빠르게 음식 세팅!"},
    {"rank": "R", "title": "🔍 오류 찾아내는 매의 눈", "power": 65, "desc": "PPT 오타와 계산 오류 0.1초 만에 포착!"},
    {"rank": "R", "title": "🎤 리허설 전담 스피치 진행자", "power": 64, "desc": "실전처럼 연습시키는 열정 전문가!"},
    {"rank": "R", "title": "📸 팀원들의 모범적인 샷 작가", "power": 63, "desc": "인생샷 하나는 무조건 건져주는 능력!"},
    {"rank": "R", "title": "🔋 인간 보조배터리 수혈자", "power": 62, "desc": "폰 배터리 1%일 때 구세주처럼 등장!"},
    {"rank": "R", "title": "🎧 소음 속 몰입 플레이어", "power": 61, "desc": "주변이 시끄러워도 내 할 일 완벽 집중!"},
    {"rank": "R", "title": "🍔 간식 창고 무한 제공자", "power": 60, "desc": "가방에서 끊임없이 과자가 나오는 마술사!"},
    {"rank": "R", "title": "🧼 청결하고 깔끔한 정리정돈왕", "power": 59, "desc": "팀원들 책상 위를 쾌적하게 싹 청소!"},
    {"rank": "R", "title": "🏃‍♂️ 필요한 재료 5초 출동 달리기", "power": 58, "desc": "문구류 사 오기 미션 단숨에 완료!"},

    # 4. N 등급 - 반전 매력 & 아슬아슬 포텐 (10종)
    {"rank": "N", "title": "🌸 야식 메뉴 결정장애", "power": 57, "desc": "메뉴 고르다가 제한시간 다 보냄!"},
    {"rank": "N", "title": "🍧 발표 도중 3초 얼음", "power": 56, "desc": "어... 내가 방금 무슨 말 했지?"},
    {"rank": "N", "title": "🎀 벼락치기 1분 전 기적", "power": 55, "desc": "제출 직전에 완성하는 아슬아슬함!"},
    {"rank": "N", "title": "🍡 귀여운 분위기 마스코트", "power": 54, "desc": "존재 자체만으로 팀원들 힐링 부여!"},
    {"rank": "N", "title": "😴 눈뜨고 조는 스킬 보유자", "power": 53, "desc": "선생님 눈은 피하지만 경청하는 척!"},
    {"rank": "N", "title": "🍬 주머니 속 사탕 나눠주는 천사", "power": 52, "desc": "달콤함으로 팀원들 사기 충천!"},
    {"rank": "N", "title": "📱 쇼츠 보다가 1시간 순삭", "power": 51, "desc": "잠깐 휴식인데 유행 밈 마스터 되어서 돌아옴!"},
    {"rank": "N", "title": "🎈 무한 긍정 행복회로 가동자", "power": 50, "desc": "점수 떨어져도 '오히려 좋아!' 외침!"},
    {"rank": "N", "title": "🐣 아직은 모든 게 싱그러운 루키", "power": 49, "desc": "배우려는 의지만큼은 열정 폭발!"},
    {"rank": "N", "title": "🍀 행운에 모든 걸 건 서바이벌러", "power": 48, "desc": "능력치는 낮아도 운으로 뽀록 승리 노림!"},
]

# CSS 모바일 스타일링
st.markdown(
    """
    <style>
    .stApp { background-color: #0F1016; color: white; }
    .block-container { padding-top: 0.8rem !important; padding-bottom: 0.8rem !important; }
    
    .main-title { 
        text-align: center; 
        font-size: 1.4rem !important; 
        font-weight: 800; 
        color: #FFD166; 
        margin-bottom: 10px !important; 
        text-shadow: 0 2px 8px rgba(255,209,102,0.3);
    }
    
    div[data-testid="stExpander"] { background-color: #181925 !important; border: 1px solid #333446 !important; border-radius: 14px !important; }
    div[data-testid="stExpander"] summary { background-color: #232538 !important; color: #FFD166 !important; font-weight: bold !important; font-size: 0.9rem !important; }
    
    .card-SSR { background: linear-gradient(135deg, #FFF3B0, #CA8A04); color: #1E1B4B; border-radius: 14px; padding: 12px; text-align: center; font-weight: 800; border: 2px solid #FEF08A; box-shadow: 0 4px 15px rgba(202, 138, 4, 0.4); }
    .card-SR { background: linear-gradient(135deg, #DDD6FE, #7C3AED); color: #FFFFFF; border-radius: 14px; padding: 12px; text-align: center; font-weight: 800; box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4); }
    .card-R { background: linear-gradient(135deg, #A7F3D0, #059669); color: #064E3B; border-radius: 14px; padding: 12px; text-align: center; font-weight: 800; box-shadow: 0 4px 15px rgba(5, 150, 105, 0.4); }
    .card-N { background: linear-gradient(135deg, #FBCFE8, #DB2777); color: #FFFFFF; border-radius: 14px; padding: 12px; text-align: center; font-weight: 800; box-shadow: 0 4px 15px rgba(219, 39, 119, 0.4); }

    .match-card { background-color: #181925; border: 1px solid #2E3148; border-radius: 12px; padding: 12px; margin-bottom: 8px; font-size: 0.95rem; }
    .ladder-anim { background-color: #232538; border: 2px solid #FFD166; border-radius: 14px; padding: 15px; text-align: center; font-size: 1.1rem; font-weight: bold; color: #FFD166; margin-bottom: 12px; }
    .wait-box { background-color: #181925; border: 2px dashed #FFD166; border-radius: 12px; padding: 12px; text-align: center; font-size: 0.95rem; color: #FFD166; font-weight: bold; }
    
    div.stButton > button { background: linear-gradient(135deg, #06D6A0, #118AB2) !important; color: #ffffff !important; font-size: 0.95rem !important; font-weight: bold !important; border-radius: 30px !important; border: none !important; padding: 8px 16px !important; box-shadow: 0 3px 10px rgba(6, 214, 160, 0.3) !important; }
    div.stButton > button[kind="secondary"] { background: linear-gradient(135deg, #FF70A6, #FF5964) !important; color: #ffffff !important; }
    
    .start-btn button { background: linear-gradient(135deg, #FFD166, #FF9F1C) !important; color: #121212 !important; font-size: 1.25rem !important; font-weight: 800 !important; padding: 12px !important; border-radius: 30px !important; box-shadow: 0 4px 15px rgba(255, 209, 102, 0.4) !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='main-title'>🎉 2026 YUnicorn 루키톤<br>능력치 가챠 토너먼트 서바이벌</div>",
    unsafe_allow_html=True,
)

if "last_seen_update" not in st.session_state:
    st.session_state["last_seen_update"] = 0
if "my_name" not in st.session_state:
    st.session_state["my_name"] = ""

# ----------------------------------------------------
# [1] 내 이름 등록 & 가챠 능력치 뽑기
# ----------------------------------------------------
with st.expander(
    "🙋‍♂️ 내 이름 등록 & 능력치 카드 뽑기",
    expanded=not game_state["is_game_started"],
):
    col_host_check, _ = st.columns([3, 1])
    is_host = col_host_check.checkbox(
        "👑 방장(진행자) 접속",
        value=(st.session_state["my_name"] == "방장"),
    )

    if is_host:
        st.session_state["my_name"] = "방장"
        st.info("👑 방장(진행자) 권한 접속: 게임 생성 및 경기 진행 가능")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            input_name = st.text_input(
                "이름 입력",
                value=(
                    ""
                    if st.session_state["my_name"] == "방장"
                    else st.session_state["my_name"]
                ),
                placeholder="본인 이름 입력",
                label_visibility="collapsed",
            )
        with col2:
            if st.button("🎲 뽑기!", use_container_width=True):
                if input_name and input_name != "방장":
                    st.session_state["my_name"] = input_name
                    drawn = random.choice(GACHA_CARDS)
                    game_state["players"][input_name] = {
                        "card": drawn,
                        "power": drawn["power"] + random.randint(-4, 4),
                    }
                    game_state["last_update"] = time.time()
                    st.rerun()

    my_name = st.session_state["my_name"]
    if my_name in game_state["players"]:
        p_info = game_state["players"][my_name]
        card = p_info["card"]
        st.markdown(
            f"""
            <div class='card-{card['rank']}'>
                [{card['rank']} 등급] {card['title']}<br>
                ⚔️ 전투력: {p_info['power']} P<br>
                <small>"{card['desc']}"</small>
            </div>
        """,
            unsafe_allow_html=True,
        )

    if game_state["players"]:
        st.write(
            f"**현재 등록 선수단 ({len(game_state['players'])}명 접속 중):**"
        )
        p_tags = " ".join(
            [
                f"`👤 {p}({info['card']['rank']})`"
                for p, info in game_state["players"].items()
            ]
        )
        st.markdown(p_tags)

        if (is_host or my_name == "방장") and st.button(
            "🧹 전체 선수단 초기화", type="secondary"
        ):
            game_state["players"] = {}
            game_state["tournament_tree"] = []
            game_state["match_results"] = []
            game_state["is_game_started"] = False
            game_state["is_simulating"] = False
            game_state["champion"] = ""
            game_state["last_update"] = time.time()
            st.rerun()

st.divider()


# ----------------------------------------------------
# [2] 대진표 무작위 자동 생성 함수 (방장 전용)
# ----------------------------------------------------
def build_tournament_tree():
    players_list = list(game_state["players"].keys())
    random.shuffle(players_list)

    tree = []
    for i in range(0, len(players_list), 2):
        if i + 1 < len(players_list):
            tree.append([players_list[i], players_list[i + 1]])
        else:
            tree.append([players_list[i], "🍀 부전승"])

    game_state["tournament_tree"] = tree
    game_state["match_results"] = []
    game_state["is_game_started"] = True

    n = len(players_list)
    if n > 32:
        game_state["current_round_name"] = f"🔥 {n}강전 (대규모 서바이벌)"
    elif n > 16:
        game_state["current_round_name"] = "⚔️ 32강전"
    elif n > 8:
        game_state["current_round_name"] = "⚔️ 16강전"
    elif n > 4:
        game_state["current_round_name"] = "💥 8강전"
    elif n > 2:
        game_state["current_round_name"] = "🏆 준결승전 (4강)"
    else:
        game_state["current_round_name"] = "🌟 대망의 결승전 🌟"

    game_state["last_update"] = time.time()


# 게임 시작 전 컨트롤 영역
if not game_state["is_game_started"]:
    if is_host or my_name == "방장":
        if len(game_state["players"]) < 2:
            st.warning(
                "⚠️ 최소 2명 이상의 학생이 카드를 뽑아야 대진표를 만들 수 있습니다."
            )
        else:
            st.markdown("<div class='start-btn'>", unsafe_allow_html=True)
            if st.button(
                "🚀 대진표 자동 생성 & 게임 시작!",
                use_container_width=True,
            ):
                build_tournament_tree()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='wait-box'>⏳ 방장(선생님)이 대진표를 짜고 게임을 시작할 때까지 잠시 대기해 주세요!</div>",
            unsafe_allow_html=True,
        )

# ----------------------------------------------------
# [3] 토너먼트 진행 및 사다리 승부 연출
# ----------------------------------------------------
if game_state["is_game_started"] and not game_state["champion"]:
    st.subheader(f"{game_state['current_round_name']}")

    # 1) 사다리 등반 시뮬레이션 애니메이션 연출 중인 경우
    if game_state["is_simulating"]:
        step = game_state["simulation_step"]
        
        # 단계별 사다리 등반 시각 연출
        anim_text = [
            "🪜 ⚡ 선수들이 출발선에서 사다리에 올라섭니다! ⚡",
            "🏃‍♂️💨 🪜 |====| 선수들이 가챠 스킬을 발동하며 사다리를 다투어 올라가는 중! |====| 🏃‍♀️💨",
            "⚔️💥 🪜 |==💥==| 정상 직전! 두 선수의 능력치가 불꽃튀게 부딪힙니다! |==💥==| ⚔️",
            "🎉 🪜 🏆 사다리 정상 도달! 승자가 가려졌습니다! 🏆"
        ]
        
        st.markdown(
            f"<div class='ladder-anim'>{anim_text[step]}<br><br><progress value='{(step+1)*25}' max='100' style='width:80%;'></progress></div>",
            unsafe_allow_html=True,
        )
        
        # 방장이 애니메이션 진행을 전역 업데이트
        if is_host or my_name == "방장":
            time.sleep(0.8)
            if step < 3:
                game_state["simulation_step"] += 1
                game_state["last_update"] = time.time()
                st.rerun()
            else:
                # 애니메이션 종료 후 실제 연산 결과 확정
                next_round = []
                results = []

                for match in game_state["tournament_tree"]:
                    p1, p2 = match[0], match[1]

                    if p2 == "🍀 부전승":
                        next_round.append(p1)
                        results.append(f"✨ [{p1}] 님 부전승으로 다음 라운드 진출!")
                    else:
                        pow1 = game_state["players"][p1]["power"]
                        pow2 = game_state["players"][p2]["power"]

                        total = pow1 + pow2
                        chance_p1 = (pow1 / total) + random.uniform(-0.15, 0.15)

                        winner = p1 if chance_p1 >= 0.5 else p2
                        loser = p2 if winner == p1 else p1

                        next_round.append(winner)
                        results.append(f"💥 [{winner}] 사다리 등반 성공 승리! (vs {loser})")

                game_state["match_results"] = results

                # 최종 1인 판정
                if len(next_round) == 1:
                    game_state["champion"] = next_round[0]
                else:
                    new_tree = []
                    for i in range(0, len(next_round), 2):
                        if i + 1 < len(next_round):
                            new_tree.append([next_round[i], next_round[i + 1]])
                        else:
                            new_tree.append([next_round[i], "🍀 부전승"])

                    game_state["tournament_tree"] = new_tree

                    n = len(next_round)
                    if n > 16:
                        game_state["current_round_name"] = "⚔️ 32강전"
                    elif n > 8:
                        game_state["current_round_name"] = "⚔️ 16강전"
                    elif n > 4:
                        game_state["current_round_name"] = "💥 8강전"
                    elif n > 2:
                        game_state["current_round_name"] = "🏆 준결승전 (4강)"
                    else:
                        game_state["current_round_name"] = "🌟 대망의 결승전 🌟"

                game_state["is_simulating"] = False
                game_state["last_update"] = time.time()
                st.rerun()

    # 2) 대진표 상태 (경기 시작 전)
    else:
        # 대진표 표시 및 사다리 위치
        for idx, match in enumerate(game_state["tournament_tree"]):
            p1, p2 = match[0], match[1]
            st.markdown(
                f"<div class='match-card'><b>[MATCH {idx+1}]</b> 👤 {p1} <span style='color:#FFD166;'>🪜====🪜</span> 👤 {p2}</div>",
                unsafe_allow_html=True,
            )

        if is_host or my_name == "방장":
            st.markdown("<div class='start-btn'>", unsafe_allow_html=True)
            if st.button(
                "🪜 사다리 대결 진행! (애니메이션 출발)",
                use_container_width=True,
            ):
                game_state["is_simulating"] = True
                game_state["simulation_step"] = 0
                game_state["last_update"] = time.time()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div class='wait-box'>⏳ 방장(선생님)이 사다리 출발 버튼을 누를 때까지 잠시 대기해 주세요!</div>",
                unsafe_allow_html=True,
            )

    if game_state["match_results"] and not game_state["is_simulating"]:
        st.write(" **직전 라운드 대결 결과:**")
        for r in game_state["match_results"]:
            st.success(r)

# ----------------------------------------------------
# [4] 단 1명의 최종 우승자 연출
# ----------------------------------------------------
if game_state["champion"]:
    st.balloons()
    champ = game_state["champion"]
    card = game_state["players"][champ]["card"]

    st.markdown(
        f"""
        <div style='background: linear-gradient(135deg, #FFD166, #FF9F1C); padding: 25px; border-radius: 20px; text-align: center; color: #121212; font-weight: bold;'>
            <h1>🏆 사다리 정상 도달! 최종 우승 🏆</h1>
            <h2 style='font-size: 2.5rem;'>👤 {champ} 님</h2>
            <p style='font-size: 1.2rem;'>[{card['rank']} 등급] {card['title']}</p>
            <p style='font-size: 1.1rem;'>✨ 2026 YUnicorn 루키톤 최강의 창업가 등극! ✨</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    if is_host or my_name == "방장":
        if st.button(
            "🔄 새 게임 다시 하기",
            type="secondary",
            use_container_width=True,
        ):
            game_state["players"] = {}
            game_state["tournament_tree"] = []
            game_state["match_results"] = []
            game_state["is_game_started"] = False
            game_state["is_simulating"] = False
            game_state["champion"] = ""
            game_state["last_update"] = time.time()
            st.rerun()

# ----------------------------------------------------
# [5] 초고속 실시간 일괄 동기화 (0.1초 하트비트)
# ----------------------------------------------------
if st.session_state["last_seen_update"] != game_state["last_update"]:
    st.session_state["last_seen_update"] = game_state["last_update"]
    st.rerun()

time.sleep(0.1)
st.rerun()