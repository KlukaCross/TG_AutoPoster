import argparse
import datetime
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger as log

from .TG_AutoPoster import AutoPoster
from .utils.vk.main import main

if os.name != "nt":
    TEMP_DIR = TemporaryDirectory(prefix="TG_AutoPoster")
    CACHE_DIR = Path(TEMP_DIR.name)
else:
    CACHE_DIR = Path.cwd() / ".cache"
CONFIG_PATH = Path.cwd() / "config.yaml"


def create_parser():
    parser = argparse.ArgumentParser(
        prog="TG_AutoPoster",
        description="Telegram Bot for AutoPosting from VK",
        epilog="(C) 2018-2022 Adrian Polyakov\nReleased under the MIT License.",
    )

    parser.add_argument(
        "-6",
        "--ipv6",
        action="store_true",
        help="Использовать IPv6 при подключении к Telegram (IPv4 по умолчанию)",
    )
    parser.add_argument(
        "-l",
        "--loop",
        action="store_const",
        const=True,
        default=False,
        help="Запустить бота в бесконечном цикле с проверкой постов раз в час (по умолчанию)",
    )
    parser.add_argument(
        "-s",
        "--sleep",
        type=int,
        default=0,
        help="Проверять новые посты каждые N секунд",
        metavar="N",
    )
    parser.add_argument(
        "-c",
        "--config",
        default=CONFIG_PATH,
        help="Абсолютный путь к конфиг файлу бота (по умолчанию {})".format(
            CONFIG_PATH
        ),
    )
    parser.add_argument(
        "--cache-dir",
        default=CACHE_DIR,
        help="Абсолютный путь к папке с кэшем бота (по умолчанию используется временная папка; .cache в Windows)",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Режим отладки")
    return parser


if __name__ == "__main__":
    args = create_parser().parse_args()

    if args.debug:
        log.add(
            "logs/bot_log_{time}_DEBUG.log",
            level="DEBUG",
            backtrace=True,
            diagnose=True,
            rotation="daily",
            retention=2,
        )
    else:
        log.remove()
        log.add(
            "logs/bot_log_{time}.log",
            rotation="daily",
            retention="3 days",
            compression="zip",
        )

    log.info("TG_AutoPoster запущен")
    client = AutoPoster(
        config_path=args.config,
        ipv6=args.ipv6,
    )

    loop = False
    sleep_time = 3600
    if args.loop or args.sleep:
        loop = True
        sleep_time = args.sleep if args.sleep else sleep_time
    elif os.getenv("TG_SLEEP") or os.getenv("TG_LOOP"):
        loop = True
        try:
            sleep_time = int(os.getenv("TG_SLEEP"))
        except ValueError:
            sleep_time = 3600

    if loop:
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=main,
            trigger="interval",
            seconds=sleep_time,
            args=(
                client,
                Path(args.config),
                Path(args.cache_dir),
            ),
            max_instances=1,
            next_run_time=datetime.datetime.now(),
        )
        scheduler.start()
        client.run()
    else:
        with client:
            main(
                client,
                Path(args.config),
                Path(args.cache_dir),
            )
