# Puzzle Alarm App - Design.md

# 개요

Puzzle Alarm은 퍼즐을 해결해야만 알람을 해제할 수 있는 안드로이드 알람 앱이다.

앱은 Kivy로 개발하며 Android APK를 목표로 한다.

불필요한 기능 없이 단순하고 빠르게 동작하는 것이 목표이다.

---

# 핵심 기능

- 알람은 한 번에 하나만 존재한다.
- 여러 개의 알람을 생성할 수 없다.
- 기존 알람 시간을 수정하는 방식이다.
- 알람 On / Off 가능
- 퍼즐을 모두 해결해야 알람 종료
- 퍼즐 종류 및 개수 사용자 설정 가능
- 사용자 지정 알람음 사용 가능

---

# 첫 실행

앱을 처음 실행하면 아래 기본 설정을 자동 생성한다.

Alarm Time
- 07:00 AM

Alarm
- ON

Puzzle
- Math

Puzzle Count
- 1

Sound
- Default

설정 파일(settings.json)이 존재하지 않으면 자동 생성한다.

---

# 화면 구성

## Home Screen

표시

- 현재 알람 시간
- Alarm ON/OFF Switch

하단 버튼

- Alarm Settings

알람이 울리는 경우

하단 버튼이

Puzzle Solve

버튼으로 변경된다.

---

## Alarm Settings

설정 가능한 항목

Alarm Time

- Hour
- Minute

Puzzle Type

- Math
- Color
- Typing

Puzzle Count

- 1 ~ 5

Alarm Sound

- Default
- Custom MP3

Save

Cancel

---

## Puzzle Screen

알람이 울리면 진입.

알람음은 퍼즐 화면 진입과 동시에 일시 정지된다.

사용자가

15초 동안

아무 입력도 하지 않으면

알람음을 다시 재생한다.

퍼즐 성공 시

다음 퍼즐

또는

Complete Screen

으로 이동.

---

## Complete Screen

가운데

완료

텍스트 출력

3초 유지

자동으로 Home으로 이동

---

# 알람 동작

사용자가 설정한 시간이 되면

알람음 재생

↓

Home Screen

↓

Puzzle Solve 버튼 표시

↓

사용자가 버튼 클릭

↓

Puzzle Screen

↓

알람음 일시 정지

↓

퍼즐 해결

↓

남은 퍼즐 존재

↓

다음 퍼즐

↓

모든 퍼즐 완료

↓

Complete Screen

↓

3초

↓

Home Screen

---

# 퍼즐

총 3종

매 알람마다

사용자가 선택한 종류만 사용한다.

---

## Math Puzzle

간단하지만 헷갈리는 계산 문제

예시

27 + 48 - 19

16 × 3 - 12

125 ÷ 5 + 17

랜덤 생성

객관식 사용 안 함

직접 입력

---

## Color Puzzle

비슷한 색 타일 중

다른 색 하나 찾기

예시

연핑크 35개

조금 더 진한 핑크 1개

정답 클릭

---

## Typing Puzzle

제시 문장을

띄어쓰기 포함

완전히 동일하게 입력

예시

"오늘도 목표를 달성하자."

문자 하나라도 다르면 오답

---

# 퍼즐 개수

사용자 설정

최소

1

최대

5

완료해야만 알람 종료

---

# 퍼즐 실패

오답

↓

현재 퍼즐 다시

---

# 퍼즐 화면 이탈

퍼즐 해결 전

뒤로가기

홈 이동

다른 Screen 이동

불가

사용자가 퍼즐을 모두 해결해야만

Puzzle Screen 종료

---

# 알람음

기본 알람음 제공

사용자는

MP3 선택 가능

선택한 파일 경로를

settings.json에 저장

---

# 데이터 저장

settings.json

저장 항목

alarm_hour

alarm_minute

enabled

puzzle_type

puzzle_count

sound_path

---

# 앱 종료 후

모든 설정 유지

다음 실행 시

settings.json 불러오기

---

# UI 디자인 원칙

- Material 스타일
- 심플한 디자인
- 불필요한 애니메이션 없음
- 세로 모드 전용
- 큰 버튼
- 큰 글씨
- 최소한의 화면 전환

---

# Screen 구성

HomeScreen

SettingsScreen

PuzzleScreen

CompleteScreen
