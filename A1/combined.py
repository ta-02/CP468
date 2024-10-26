import heapq
from random import shuffle
from typing import Callable, List, Optional, Tuple

EMPTY_VAL = 0
DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def generate_goal_state(n: int) -> List[List[int]]:
    return [[n * i + j for j in range(n)] for i in range(n)]


def is_solvable(puzzle: List[int]) -> bool:
    dp_count = 0
    for i in range(len(puzzle) - 1):
        for j in range(i + 1, len(puzzle)):
            if (
                puzzle[i] != EMPTY_VAL
                and puzzle[j] != EMPTY_VAL
                and puzzle[i] > puzzle[j]
            ):
                dp_count += 1
    return dp_count % 2 == 0


def gen_puzzle_state(n: int) -> Optional[List[List[int]]]:
    puzzle_state = [[-1] * n for _ in range(n)]
    domain = list(range(n * n))
    shuffle(domain)

    index = 0
    for i in range(n):
        for j in range(n):
            puzzle_state[i][j] = domain[index]
            index += 1

    puzzle_flat = [num for row in puzzle_state for num in row]
    return puzzle_state if is_solvable(puzzle_flat) else None


def gen_n_puzzle_states(n: int, count: int) -> List[List[List[int]]]:
    puzzles = []
    while len(puzzles) < count:
        state = gen_puzzle_state(n)
        if state:
            puzzles.append(state)
    return puzzles


def h1(puzzle: List[List[int]], goal_state: List[List[int]]) -> int:
    misplaced_tiles = 0
    for i in range(len(puzzle)):
        for j in range(len(puzzle)):
            if puzzle[i][j] != goal_state[i][j]:
                misplaced_tiles += 1
    return misplaced_tiles


def h2(puzzle: List[List[int]], goal_state: List[List[int]]) -> int:
    total_distance = 0
    for i in range(len(puzzle)):
        for j in range(len(puzzle)):
            num = puzzle[i][j]
            goal_x, goal_y = divmod(num, len(puzzle))
            total_distance += abs(i - goal_x) + abs(j - goal_y)
    return total_distance


def serialize_state(state: List[List[int]]) -> Tuple[Tuple[int, ...], ...]:
    return tuple(tuple(row) for row in state)


def find_empty_tile(state: List[List[int]]) -> Tuple[int, int]:
    for i in range(len(state)):
        for j in range(len(state[i])):
            if state[i][j] == EMPTY_VAL:
                return i, j
    return -1, -1  # Should never happen


def a_star_search(
    h: Callable, puzzle: List[List[int]], goal_state: List[List[int]]
) -> Tuple[int, int]:
    pq = []
    g_n = 0
    h_n = h(puzzle, goal_state)
    f_n = g_n + h_n
    heapq.heappush(pq, (f_n, puzzle, g_n))
    visited = set()
    nodes_expanded = 0

    while pq:
        f_n, current_state, g_n = heapq.heappop(pq)
        nodes_expanded += 1

        state_tuple = serialize_state(current_state)
        if state_tuple in visited:
            continue
        visited.add(state_tuple)

        if current_state == goal_state:
            return nodes_expanded, g_n

        x, y = find_empty_tile(current_state)

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(current_state) and 0 <= ny < len(current_state):
                new_state = [row.copy() for row in current_state]
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]

                if serialize_state(new_state) in visited:
                    continue

                new_g_n = g_n + 1
                new_h_n = h(new_state, goal_state)
                new_f_n = new_g_n + new_h_n

                heapq.heappush(pq, (new_f_n, new_state, new_g_n))

    return nodes_expanded, -1  # Should never happen


def solve_puzzles(puzzle_size: int, output_file: str, count: int = 100) -> None:
    goal_state = generate_goal_state(puzzle_size)
    puzzles = gen_n_puzzle_states(puzzle_size, count)
    results = []

    for idx, puzzle in enumerate(puzzles, start=1):
        h1_nodes, h1_steps = a_star_search(h1, puzzle, goal_state)
        h2_nodes, h2_steps = a_star_search(h2, puzzle, goal_state)
        results.append(
            {
                "Puzzle": idx,
                "Nodes Expanded (h1)": h1_nodes,
                "Steps (h1)": h1_steps,
                "Nodes Expanded (h2)": h2_nodes,
                "Steps (h2)": h2_steps,
            }
        )

    with open(output_file, "w") as f:
        header = (
            f"{'Puzzle':<8} {'Nodes Expanded (h1)':<22} {'Steps (h1)':<12} "
            f"{'Nodes Expanded (h2)':<22} {'Steps (h2)':<12}\n"
        )
        f.write(header)
        f.write("=" * len(header) + "\n")

        for result in results:
            f.write(
                f"{result['Puzzle']:<8} {result['Nodes Expanded (h1)']:<22} "
                f"{result['Steps (h1)']:<12} {result['Nodes Expanded (h2)']:<22} "
                f"{result['Steps (h2)']:<12}\n"
            )


def main() -> None:
    solve_puzzles(3, "q1results.txt")
    solve_puzzles(4, "q2results.txt")
    solve_puzzles(5, "q3results.txt")


if __name__ == "__main__":
    main()
