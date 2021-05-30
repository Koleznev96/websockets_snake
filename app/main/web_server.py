import sys
import datetime as dt
from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask import flash
from flask_login import LoginManager
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from app.main.database_connector import DatabaseConnector
from app.forms import AuthForm
from app.forms import RegistrationForm
from app.forms import CreateEventForm
from app.main.user import User
from app.main.event import Event


class WebServer:
    """
    Класс веб-сервера.
    Обрабатывает взаимодействия пользователя с сайтом и http-запросы
    по типу регистрации, авторизации, записи на событие, отмены записи и т.п..
    """

    def __init__(self, application: Flask, db_connector: DatabaseConnector,
                 login_manager: LoginManager):
        """
        Инициализатор класса.
        :param application: Ссылка на работающее Flask-приложение.
        """

        self.__db_connector = db_connector
        self.__app = application
        self.__login_manager = login_manager

        # Запускаем обработчики GET-запросов.
        self.index = self.__app.route("/")(self.__index)
        self.profile = self.__app.route("/profile")(self.__profile)
        self.settings_profile = self.__app.route("/settings_profile")(self.__settings_profile)
        self.login = self.__app.route("/auth", methods=["GET", "POST"])(self.__login)
        self.logout = self.__app.route("/logout")(self.__logout)
        self.registration = self.__app.route("/reg", methods=["GET", "POST"])(self.__registration)
        self.broadcast = self.__app.route("/broadcast/<room>")(self.__broadcast)
        self.admin = self.__app.route("/admin")(self.__admin)
        self.creating_events = self.__app.route("/creating_events", methods=["GET", "POST"])(self.__creating_events)
        self.rules = self.__app.route("/rules")(self.__rules)
        self.register_an_event = self.__app.route("/reg_an_event/<event_name>")(self.__register_an_event)
        self.unregister_event = self.__app.route("/unreg/<event_name>")(self.__unregister_an_event)
        self.event = self.__app.route("/event/<event_name>")(self.__event)
        self.load_file = self.__app.route("/load_file/<event_name>", methods=["GET", "POST"])(self.__load_file)

    @login_required
    def __unregister_an_event(self, event_name):
        """Метод отмены регистрации юзера на заданное событие"""

        # FIXME: Сделать нормальные именя методов, полностью отображающие их ф-ии.
        if self.__db_connector.validate_event(event_name):
            flash("Такого события не существует.", "error")
            # Проверка на существование события.
        elif not self.__db_connector.event_open_for_registration(event_name):
            # Проверка, что от события еще можно отписаться без
            # записи результатов юзера в этом событии.
            flash("Это событие уже началось.", "error")
        elif not self.__db_connector.user_in_event(current_user.get_name(), event_name):
            # Проверка, что данный юзер есть в этом событии.
            flash("Вы не зарегистрированы на это событие.", "error")
        else:
            # Если все проверки пройдены, отменяем регистрацию юзера на событие.
            self.__db_connector.unregister_user_from_event(current_user.get_name(), event_name)
            flash("Регистрация успешно отменена!", "success")

        return redirect(url_for("__profile"))

    @login_required
    def __register_an_event(self, event_name):
        """Метод регистрации юзера на событие"""

        # Проверки на доступ к регистрации.
        if self.__db_connector.user_in_event(current_user.get_name(), event_name):
            flash("Вы не можете зарегистрироваться на это событие.", "error")
            return redirect(url_for("__index"))
        if not self.__db_connector.event_open_for_registration(event_name):
            flash("На это событие больше нельзя зарегистрироваться.", "error")
            return redirect(url_for("__index"))

        # Если проверки пройдены, регаем.
        self.__db_connector.register_user_to_event(current_user.get_name(), event_name)

        return redirect(url_for("__profile"))

    @login_required
    def __index(self):
        events = self.__db_connector.get_all_events()
        return render_template("index.html", events=events)

    @login_required
    def __admin(self):
        # TODO: доступ только админам.
        return render_template("administration.html")

    @login_required
    def __creating_events(self):
        """Создание событий"""
        # TODO: доступ только админам.
        form = CreateEventForm()
        if form.validate_on_submit():
            if self.__db_connector.validate_event(form.name.data):
                date = form.date.data
                time = form.time.data
                event_run_date = dt.datetime(date.year, date.month, date.day,
                                             time.hour, time.minute)
                new_event = Event(name=form.name.data,
                                  organizer=form.organizer.data,
                                  type_game=form.type_game.data,
                                  mode_game=form.mode_game.data,
                                  max_count_users=form.max_count_users.data,
                                  current_count_users=0,
                                  run_date=event_run_date,
                                  duration=form.duration.data,
                                  broadcast_avail=form.broadcast_avail.data,
                                  record_avail=form.record_avail.data)
                self.__db_connector.register_event(new_event)
                flash("Событие создано! :)", "success")
            else:
                flash("Такая тусовка у нас уже есть!", "error")
        return render_template("creating_events.html", form=form)

    @login_required
    def __rules(self):
        # TODO: доступ только админам.
        return render_template("rules.html")

    @login_required
    def __profile(self):
        # Список событий, на которые зареган юзер.
        user_events = self.__db_connector.get_user_events(current_user.get_name())
        return render_template("user.html", events=user_events)

    @login_required
    def __settings_profile(self):
        return render_template("settings.html")

    def __login(self):
        """Метод обработки запросов пользователя на странице авторизации"""
        if current_user.is_authenticated:
            return redirect(url_for("__index"))

        form = AuthForm()

        # Если пришел POST запрос в форме, обрабатываем его.
        if form.validate_on_submit():
            # Загружаем юзера со всеми его данными.
            user = self.__db_connector.load_user(form.name.data)

            # Если юзер вошел, перенаправляем на главную.
            if user and user.verify_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect(request.args.get("next") or url_for("__index"))
            else:
                flash("Упс, похоже, вы ошиблись с данными.", "error")

        # Если юзер не смог войти или просто открыл страницу авторизации,
        # отправляем шаблон с формой.
        return render_template("authorization.html", form=form)

    @login_required
    def __logout(self):
        """Метод удаления пользователя из сеанса в системе"""
        logout_user()
        flash("Возвращайтесь к нам еще ^-^", "success")
        return redirect(url_for("__login"))

    def __registration(self):
        """Обработка регистарции пользователя"""
        if current_user.is_authenticated:
            return redirect(url_for("__index"))

        form = RegistrationForm()

        # Если пришел POST запрос в форме, обрабатываем его.
        if form.validate_on_submit():
            # Если юзера нет в БД, т.е. его имя уникально.
            if self.__db_connector.validate_username(form.name.data):
                # user_id присваивается при непосредственном входе юзера в систему.
                # Т.е. в методе login. В базе данных id присваивается автоматически.
                new_user = User(name=form.name.data,
                                password=form.password.data,
                                role="user",
                                hashing=True)

                # Добавляем в БД и перенаправляем на страницу входа.
                self.__db_connector.register_user(new_user)
                flash("Ура! Теперь ты можешь войти!", "success")
                return redirect(url_for("__login"))
            else:
                flash("Кто ты? Пользователь с таким именем уже существует!", "error")
        elif form.password.errors:
            flash(form.password.errors[0], "error")

        return render_template("registration.html", form=form)

    @login_required
    def __event(self, event_name):
        """Рендеринг страницы события и загрузки решения"""
        event = self.__db_connector.load_event(event_name=event_name)

        if not event or event.get_run_date() >= dt.datetime.now():
            flash("Событие еще не началось.", "error")
            return redirect(url_for("__profile"))
        if not self.__db_connector.user_in_event(current_user.get_name(), event_name):
            flash("Вы не зарегистрированны на это событие.")
            return redirect(url_for("__index"))

        return render_template("loading.html", event=event)

    @login_required
    def __broadcast(self, room):
        """Рендеринг страницы трансляции со всеми необходимыми данными"""
        # Отсылаем клиенту данные для подключения к комнате в сокет-сервере.
        # Это имя пользователя и название комнаты, которое передается в GET-запросе.
        data_for_connect = {"username": current_user.get_name(),
                            "room": room}
        return render_template("broadcast.html", data=data_for_connect)

    @login_required
    def __load_file(self, event_name):
        """Метод загрузки решения юзера"""
        # TODO: Сделать проверку файла на безопасноть.
        event = self.__db_connector.load_event(event_name=event_name)
        if request.method == "POST":
            file = request.files["file"]
            file.save(sys.path[0] + f"/app/rooms/{event_name}/{current_user.get_name()}.py")
            flash("Решение успешно загружено!", "success")
        return render_template("loading.html", event=event)
