import heapq
from random import shuffle
from typing import Callable, List, Optional, Tuple

EMPTY_VAL = 0
DOMAIN = list(range(25))
GOAL_STATE = [
    [0, 1, 2, 3, 4],
    [5, 6, 7, 8, 9],
    [10, 11, 12, 13, 14],
    [15, 16, 17, 18, 19],
    [20, 21, 22, 23, 24],
]
DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def is_solvable(puzzle: List[int]) -> bool:
    inv_count = 0
    for i in range(24):
        for j in range(i + 1, 25):
            if (
                puzzle[i] != EMPTY_VAL
                and puzzle[j] != EMPTY_VAL
                and puzzle[i] > puzzle[j]
            ):
                inv_count += 1
    return inv_count % 2 == 0


def gen_twentyfour_puzzle_state() -> Optional[List[List[int]]]:
    puzzle_state = [[-1] * 5 for _ in range(5)]
    domain = DOMAIN[:]
    shuffle(domain)

    index = 0
    for i in range(5):
        for j in range(5):
            puzzle_state[i][j] = domain[index]
            index += 1

    puzzle_flat = [num for row in puzzle_state for num in row]
    return puzzle_state if is_solvable(puzzle_flat) else None


def gen_100_twentyfour_puzzle_states() -> List[List[List[int]]]:
    num_puzzles = 0
    puzzle_states = []

    while num_puzzles < 100:
        puzzle_state = gen_twentyfour_puzzle_state()
        if puzzle_state:
            puzzle_states.append(puzzle_state)
            num_puzzles += 1

    return puzzle_states


def h1(puzzle: List[List[int]]) -> int:
    misplaced_tiles = 0
    for i in range(5):
        for j in range(5):
            if puzzle[i][j] != GOAL_STATE[i][j]:
                misplaced_tiles += 1
    return misplaced_tiles


def h2(puzzle: List[List[int]]) -> int:
    total_manhattan_distance = 0
    for i in range(5):
        for j in range(5):
            num = puzzle[i][j]
            goal_x, goal_y = divmod(num, 5)
            total_manhattan_distance += abs(i - goal_x) + abs(j - goal_y)
    return total_manhattan_distance


def h3(puzzle: List[List[int]]) -> int:
    out_of_row = 0
    out_of_column = 0
    for i in range(5):
        for j in range(5):
            num = puzzle[i][j]
            goal_i, goal_j = divmod(num, 5)
            if i != goal_i:
                out_of_row += 1
            if j != goal_j:
                out_of_column += 1
    return out_of_row + out_of_column


def serialize_state(state: List[List[int]]) -> Tuple[Tuple[int, ...], ...]:
    return tuple(tuple(row) for row in state)


def find_empty_tile(state: List[List[int]]) -> Tuple[int, int]:
    for i in range(5):
        for j in range(5):
            if state[i][j] == EMPTY_VAL:
                return i, j
    return -1, -1


def a_star_search(
    h: Callable[[List[List[int]]], int], puzzle: List[List[int]]
) -> Tuple[int, int]:
    pq = []
    g_n = 0
    h_n = h(puzzle)
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

        if current_state == GOAL_STATE:
            return nodes_expanded, g_n

        x, y = find_empty_tile(current_state)

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 5 and 0 <= ny < 5:
                new_state = [row.copy() for row in current_state]
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]

                new_state_tuple = serialize_state(new_state)
                if new_state_tuple in visited:
                    continue

                new_g_n = g_n + 1
                new_h_n = h(new_state)
                new_f_n = new_g_n + new_h_n

                heapq.heappush(pq, (new_f_n, new_state, new_g_n))

    return nodes_expanded, -1


def main() -> None:
    puzzles = gen_100_twentyfour_puzzle_states()
    results = []

    for idx, puzzle in enumerate(puzzles, start=1):
        h1_nodes, h1_steps = a_star_search(h1, puzzle)
        h2_nodes, h2_steps = a_star_search(h2, puzzle)
        h3_nodes, h3_steps = a_star_search(h3, puzzle)
        results.append(
            {
                "Puzzle": idx,
                "Nodes Expanded (h1)": h1_nodes,
                "Steps (h1)": h1_steps,
                "Nodes Expanded (h2)": h2_nodes,
                "Steps (h2)": h2_steps,
                "Nodes Expanded (h3)": h3_nodes,
                "Steps (h3)": h3_steps,
            }
        )

    with open("q2results.txt", "w+") as f:
        header = (
            f"{'Puzzle':<8} {'Nodes Expanded (h1)':<22} {'Steps (h1)':<12} "
            f"{'Nodes Expanded (h2)':<22} {'Steps (h2)':<12} "
            f"{'Nodes Expanded (h3)':<22} {'Steps (h3)':<12}\n"
        )
        f.write(header)
        f.write("=" * len(header) + "\n")

        for result in results:
            f.write(
                f"{result['Puzzle']:<8} {result['Nodes Expanded (h1)']:<22} "
                f"{result['Steps (h1)']:<12} {result['Nodes Expanded (h2)']:<22} "
                f"{result['Steps (h2)']:<12} {result['Nodes Expanded (h3)']:<22} "
                f"{result['Steps (h3)']:<12}\n"
            )

        total_h1_nodes = total_h1_steps = total_h2_nodes = total_h2_steps = 0
        total_h3_nodes = total_h3_steps = 0

        for result in results:
            total_h1_nodes += result["Nodes Expanded (h1)"]
            total_h1_steps += result["Steps (h1)"]
            total_h2_nodes += result["Nodes Expanded (h2)"]
            total_h2_steps += result["Steps (h2)"]
            total_h3_nodes += result["Nodes Expanded (h3)"]
            total_h3_steps += result["Steps (h3)"]

        avg_h1_nodes = total_h1_nodes / len(results)
        avg_h1_steps = total_h1_steps / len(results)
        avg_h2_nodes = total_h2_nodes / len(results)
        avg_h2_steps = total_h2_steps / len(results)
        avg_h3_nodes = total_h3_nodes / len(results)
        avg_h3_steps = total_h3_steps / len(results)

        f.write("\nAverages:\n")
        f.write(f"{'Average Nodes Expanded (h1):':<30} {avg_h1_nodes:.2f}\n")
        f.write(f"{'Average Steps (h1):':<30} {avg_h1_steps:.2f}\n")
        f.write(f"{'Average Nodes Expanded (h2):':<30} {avg_h2_nodes:.2f}\n")
        f.write(f"{'Average Steps (h2):':<30} {avg_h2_steps:.2f}\n")
        f.write(f"{'Average Nodes Expanded (h3):':<30} {avg_h3_nodes:.2f}\n")
        f.write(f"{'Average Steps (h3):':<30} {avg_h3_steps:.2f}\n")


if __name__ == "__main__":
    main()
