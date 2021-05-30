def user_algorithm(playing_field):
    distance = {}
    snake_head = {}
    apple = {}
    stenka = []
    direction = ""
    for y in range(len(playing_field)):
        for x in range(len(playing_field[0])):
            if playing_field[y][x] == 3:
                snake_head = {"x": x, "y": y}
            elif playing_field[y][x] == 2:
                apple = {"x": x, "y": y}
            elif not playing_field[y][x] == 0:
                stenka.append({"x": x, "y": y})

    distance = {"x": snake_head["x"] - apple["x"],
                "y": snake_head["y"] - apple["y"]}

    not_direction = []

    for i in stenka:
        if snake_head["x"] + 1 == i["x"] and snake_head["y"] == i["y"]:
            not_direction.append("right")
        if snake_head["x"] - 1 == i["x"] and snake_head["y"] == i["y"]:
            not_direction.append("left")
        if snake_head["x"] == i["x"] and snake_head["y"] - 1 == i["y"]:
            not_direction.append("up")
        if snake_head["x"] == i["x"] and snake_head["y"] + 1 == i["y"]:
            not_direction.append("down")

    if abs(distance["x"]) > abs(distance["y"]):
        if distance["x"] < 0:
            direction = "right"
        else:
            direction = "left"
    else:
        if distance["y"] < 0:
            direction = "down"
        else:
            direction = "up"

    list_direction = ["right", "left", "down", "up"]
    if direction in not_direction:
        direction = ""
        for el in list_direction:
            if not (el in not_direction):
                direction = el
                break

    if not direction:
        direction = "up"

    return direction
