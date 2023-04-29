names: list[str] = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
name_taken: list[bool] = [False] * len(names)


def get_not_taken_name() -> str:
    for i in range(ord('Z') - ord('A') + 1):
        if not name_taken[i]:
            name_taken[i] = True
            return names[i]


def free_name(name: str) -> None:
    name_taken[ord(name) - ord('A')] = False
