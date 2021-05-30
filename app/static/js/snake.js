var username = "";
var room = "";
var socket = io();
var client_sid;

document.getElementById("btn_connect").onclick = function () {
    // Подключение
    username = document.getElementById("input_name").value;
    if (username == "") {
        alert("Enter the your name!");
        return;
    }
    room = document.getElementById("input_room").value;
    if (username == "") {
        alert("Enter the room which you want connected!");
        return;
    }
    client_sid = socket.id;
    socket.emit("join", {sid: client_sid, username: username, room: room});
}

socket.on("disconnect", function () {
    socket.emit("leave", {sid: client_sid, username: username, room: room});
});

document.getElementById("btn_disconnect").onclick = function () {
    socket.emit("leave", {sid: client_sid, username: username, room: room});
}

let data_from_server;

// Ширина канваса
const CANVAS_WIDTH = 612
// Высота канваса
const CANVAS_HEIGHT = 612

// Расстояние между ячейками.
const CELL_MARGIN = 3
// Внутренние отступы канваса.
const GAME_PADDING = 10

// Цвет ячейки стенки.
const LET_COLOR = '#22261e'
// Цвет ячейки с едой. (Apple green)
const FOOD_COLOR = '#8db600'
// Цвет тела змейки. (Eden)
const SNAKE_COLOR_BODY = '#264e36'
// Цвет головы змейки. (Eden)
const SNAKE_COLOR_HEAD = '#981815'
// Цвет пустых ячеек.
const FREE_COLOR = 'rgb(240, 240, 240)'

const canvas = document.getElementById("game");
const context = canvas.getContext('2d');

const COLOR_SNAKES = ['#1b1bb3', '#ffcd00', '#ff2c00', '#8db600', '#c9007a'];

let color_users = {};

// Размеры канваса.
canvas.width = CANVAS_WIDTH
canvas.height = CANVAS_HEIGHT

function drawRect (param) {
	// Новая геометрическая фигура.
	context.beginPath()
	// Обозначить прямоугольник.
	context.rect(param.x, param.y, param.width, param.height)
	context.fillStyle = param.fillColor
	context.fill()
}

// Функция очищает канвас.
function clearCanvas () {
	// Очистить канвас по канону, как предусмотрено в JS.
	context.clearRect(0, 0, canvas.width, canvas.height)
}

// Функция отрисовывает карту.
function drawGameMap (map, cel_size) {

	// Пройти по всем ячейкам.
    for (let y = 0; y < map.length; y++){
        for (let x = 0; x < map[0].length; x++) {
            const param = {
                // Координаты левого верхнего угла.
                x: GAME_PADDING + x * (cel_size + CELL_MARGIN),
                y: GAME_PADDING + y * (cel_size + CELL_MARGIN),
                // Ширина и высота прямоугольника.
                width: cel_size,
                height: cel_size,
                // Цвет заливки.
                fillColor: FREE_COLOR
            }
            // Если ячейка с едой:
            if (map[y][x].type === "apple") {
                param.fillColor = FOOD_COLOR
            }

            // Если в ячейке голова змейка:
            if (map[y][x].type === "snake_head") {
                param.fillColor = SNAKE_COLOR_HEAD
            }

            // Если в ячейке тело змейка:
            if (map[y][x].type === "snake_body") {
                param.fillColor = color_users[map[y][x].user]
            }

            // Если в ячейке стенка:
            if (map[y][x].type === "let") {
                param.fillColor = LET_COLOR
            }

            // Отрисовать выбранную ячейку.
            drawRect(param)
        }
	}
}

// Функция выводит информацию о состоянии игры.
function showState () {
	context.fillStyle = 'black'
	context.font = "20px sans-serif"
	context.textAlign = "left"
	context.fillText(`Cooldown: ${cooldown}`, 10, 30)
	context.fillText(`Очки: ${snake.length * 5}`, 10, 50)
}

function callSize(rows, columns) {
    const CANVAS_PADDING_HEIGHT = 2 * GAME_PADDING + rows * CELL_MARGIN;
    const CANVAS_PADDING_WIDTH = 2 * GAME_PADDING + columns * CELL_MARGIN;
    let size_call_height = (CANVAS_HEIGHT - CANVAS_PADDING_HEIGHT) / rows;
    let size_call_width = (CANVAS_WIDTH - CANVAS_PADDING_WIDTH) / columns;
    return Math.floor(Math.min(size_call_height, size_call_width));
}

function loop (data) {

	clearCanvas();
    let playing_field = data.playing_field;
    let data_users = data.data_users;
        for (let i = 0; i < data_users.length; i++) {
            color_users[data_users[i].user] = COLOR_SNAKES[i];
        }
    // Расчитаем размер одной клетки поля
    let cel_size = callSize(playing_field.length, playing_field[0].length);
	// Отрисовать карту игры.
	drawGameMap(playing_field, cel_size);

    // выводит информацию о состоянии игры.
	// showState()
}

socket.on("message", function (data) {
    data_from_server = JSON.parse(data);
    loop(data_from_server);
});