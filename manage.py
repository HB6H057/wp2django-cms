#!env/bin/python
from faker import Factory
from random import choice, sample, randint

from sqlalchemy import func
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server

from app import create_app
from app.core.models import db, User, Category, Post, Tag, Comment

app = create_app()

manager = Manager(app)
Migrate(app, db)

app.jinja_env.globals['Category'] = Category
app.jinja_env.globals['Post'] = Post
app.jinja_env.globals['Tag'] = Tag
app.jinja_env.globals['func'] = func

@manager.command
def forged():

    db.drop_all()
    db.create_all()

    faker = Factory.create()

    def generate_post(func_user, func_categorys, func_tags):
        return Post(title=faker.sentence(),
                    body=faker.paragraph(),
                    user=func_user(),
                    category=func_categorys(),
                    tags=func_tags())

    def generate_user():
        return User(email=faker.email(),
                    username=faker.word(),
                    nickname=faker.name(),
                    password='buyaoyongroot')

    def generate_category():
        return Category(name=faker.last_name(),
                        description=faker.sentence())

    def generate_tag():
        return Tag(name=faker.first_name())

    def generate_comment(func_post):
        return Comment(author=faker.first_name(),
                       email=faker.email(),
                       site='http://www.%s.com' % (faker.first_name()),
                       content=faker.sentence(),
                       post=func_post())

    users = [generate_user() for i in xrange(10)]
    db.session.add_all(users)

    categorys = [generate_category() for i in xrange(10)]
    db.session.add_all(categorys)

    tags = [generate_tag() for i in xrange(30)]
    db.session.add_all(tags)

    def random_user(): return choice(users)

    def random_category(): return choice(categorys)

    def random_tags(): return sample(tags, randint(1, 5))

    posts = [generate_post(random_user,
                           random_category, random_tags) for i in xrange(100)]
    db.session.add_all(posts)

    def random_post(): return choice(posts)

    comments = [generate_comment(random_post) for i in xrange(1000)]
    db.session.add_all(comments)

    db.session.commit()

if __name__ == '__main__':
    manager.add_command("runserver", Server(use_debugger=True))
    manager.add_command("db", MigrateCommand)
    manager.run()
