#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Set

N = 5
A = [1, 2, 3, 4, 5]  # 원소 표기용


def read_relation_matrix(n: int = N) -> List[List[int]]:
    """
    n x n 이진 행렬을 행 단위로 입력받아 2차원 리스트로 반환.
    각 행은 공백 구분 0/1 다섯 개. 잘못된 입력은 예외 발생.
    """
    print(f"{n}×{n} 관계행렬을 행 단위로 입력하세요 (각 행: 0/1 {n}개, 공백 구분)")
    R = []
    for i in range(n):
        line = input().strip().split()
        if len(line) != n:
            raise ValueError(f"{i+1}번째 행의 항목 개수가 {n}이 아닙니다.")
        row = []
        for j, tok in enumerate(line):
            if tok not in ("0", "1"):
                raise ValueError(f"{i+1}행 {j+1}열: 0/1이 아닙니다: {tok}")
            row.append(int(tok))
        R.append(row)
    return R


def print_matrix(M: List[List[int]], title: str = "") -> None:
    if title:
        print(title)
    for row in M:
        print(" ".join(str(x) for x in row))
    print()


def is_reflexive(R: List[List[int]]) -> bool:
    for i in range(N):
        if R[i][i] != 1:
            return False
    return True


def is_symmetric(R: List[List[int]]) -> bool:
    for i in range(N):
        for j in range(N):
            if R[i][j] != R[j][i]:
                return False
    return True


def is_transitive(R: List[List[int]]) -> bool:
    # 표준 Warshall 검사
    for i in range(N):
        for j in range(N):
            if R[i][j]:
                for k in range(N):
                    if R[j][k] and not R[i][k]:
                        return False
    return True


def is_equivalence(R: List[List[int]]) -> bool:
    return is_reflexive(R) and is_symmetric(R) and is_transitive(R)


def reflexive_closure(R: List[List[int]]) -> List[List[int]]:
    C = [row[:] for row in R]
    for i in range(N):
        C[i][i] = 1
    return C


def symmetric_closure(R: List[List[int]]) -> List[List[int]]:
    C = [row[:] for row in R]
    for i in range(N):
        for j in range(N):
            if R[i][j] == 1 or R[j][i] == 1:
                C[i][j] = 1
                C[j][i] = 1
    return C


def transitive_closure(R: List[List[int]]) -> List[List[int]]:
    # Warshall 알고리즘
    C = [row[:] for row in R]
    for k in range(N):
        for i in range(N):
            if C[i][k]:
                # 미세 최적화: C[i][k]==1인 경우만 j loop
                for j in range(N):
                    if C[k][j]:
                        C[i][j] = 1
    return C


def eq_class_of(R: List[List[int]], idx: int) -> Set[int]:
    """
    원소 A[idx] 의 동치류 { a in A | (A[idx], a) ∈ R }을 집합으로 반환.
    (동치관계라고 가정하면 좌우 구분이 무의미하지만, 일반 관계에서도 '연관된 원소'를 반환)
    """
    cls = set()
    for j in range(N):
        if R[idx][j] == 1:
            cls.add(A[j])
    return cls


def all_eq_classes(R: List[List[int]]) -> List[Set[int]]:
    """
    동치관계일 때, 서로소한 동치류들의 목록을 반환.
    """
    seen = set()
    classes = []
    for i in range(N):
        if A[i] in seen:
            continue
        C = eq_class_of(R, i)
        classes.append(C)
        seen |= C
    return classes


def report_relation_props(R: List[List[int]], label: str = "현재 관계") -> None:
    print(f"== {label} 성질 판별 ==")
    rf, sy, tr = is_reflexive(R), is_symmetric(R), is_transitive(R)
    print(f"반사성: {'만족' if rf else '불만족'}")
    print(f"대칭성: {'만족' if sy else '불만족'}")
    print(f"추이성: {'만족' if tr else '불만족'}")
    eq = rf and sy and tr
    print(f"동치관계 여부: {'동치관계' if eq else '동치관계 아님'}\n")
    if eq:
        classes = all_eq_classes(R)
        print("동치류:")
        for idx, C in enumerate(classes, 1):
            # 보기 좋게 정렬 출력
            print(f"  클래스 {idx}: {{{', '.join(map(str, sorted(C)))}}}")
        print()
    return


def compare_and_report_closure(name: str, R: List[List[int]], closure_func) -> List[List[int]]:
    print(f"== {name} 폐포 전/후 비교 ==")
    print_matrix(R, title="변환 전 관계행렬:")
    C = closure_func(R)
    print_matrix(C, title="변환 후 관계행렬:")
    report_relation_props(C, label=f"{name} 폐포 결과")
    return C


def equivalence_closure(R: List[List[int]]) -> List[List[int]]:
    """
    추가 기능:
    주어진 관계 R을 반사/대칭/추이 폐포를 모두 적용해 가장 가까운 동치관계로 변환.
    순서는 반사 → 대칭 → 추이로 1회 적용 후, 필요 시 고정점까지 반복.
    (대칭/추이 상호작용 때문에 1~2회 반복으로 충분)
    """
    C = [row[:] for row in R]
    for _ in range(3):  # 안전상 최대 3회 반복
        before = [row[:] for row in C]
        C = reflexive_closure(C)
        C = symmetric_closure(C)
        C = transitive_closure(C)
        if C == before:
            break
    return C


def main():
    try:
        R = read_relation_matrix(N)
    except Exception as e:
        print(f"입력 오류: {e}")
        return

    print()
    print_matrix(R, title="입력한 관계행렬:")

    # 1) 현재 관계 성질/동치 여부 및 동치류(가능 시)
    report_relation_props(R, label="입력 관계")

    # 2) 각 성질별 폐포 전/후 및 동치 여부/동치류
    Rc = compare_and_report_closure("반사성", R, reflexive_closure)
    Sc = compare_and_report_closure("대칭성", R, symmetric_closure)
    Tc = compare_and_report_closure("추이성", R, transitive_closure)

    # 3) 추가: 세 폐포를 모두 적용한 동치 폐포(Equivalence Closure)
    print("== 추가 기능: 동치 폐포(반사/대칭/추이 모두 만족하도록 변환) ==")
    print_matrix(R, title="동치 폐포 변환 전:")
    Ec = equivalence_closure(R)
    print_matrix(Ec, title="동치 폐포 변환 후:")
    report_relation_props(Ec, label="동치 폐포 결과")


if __name__ == "__main__":
    main()
