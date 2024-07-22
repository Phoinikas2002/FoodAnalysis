from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
import pandas as pd

# 导入config包中导入config文件中对数据库进行的配置
from config import MYSQL_HOST,MYSQL_PORT,MYSQL_USER,MYSQL_PASSWD,MYSQL_DB

app = Flask(__name__,template_folder='templates')

app.config['SECRET_KEY'] = '123456'
# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


with app.app_context():

    class FoodData(db.Model):
        __tablename__ = 'fooddata'
        mid = db.Column(db.BigInteger, primary_key=True)
        mname = db.Column(db.String(255))
        comments_num = db.Column(db.BigInteger)
        per_capita_con = db.Column(db.BigInteger)
        taste = db.Column(db.Float)
        environment = db.Column(db.Float)
        service = db.Column(db.Float)
        phone = db.Column(db.String(255))
        address = db.Column(db.String(255))
        details = db.Column(db.String(255))

    @app.route('/')
    def index():
        data = FoodData.query.all()
        df = pd.DataFrame([(d.mid, d.mname, d.comments_num, d.per_capita_con, d.taste, d.environment, d.service, d.phone, d.address, d.details) for d in data], columns=['mid', '店名', '评论', '人均消费', '口味', '环境', '服务', '电话', '地址', '详情'])
        
        # Convert columns to numeric
        df['评论'] = pd.to_numeric(df['评论'], errors='coerce')
        df['口味'] = pd.to_numeric(df['口味'], errors='coerce')
        df['环境'] = pd.to_numeric(df['环境'], errors='coerce')
        df['服务'] = pd.to_numeric(df['服务'], errors='coerce')
        df['人均消费'] = pd.to_numeric(df['人均消费'], errors='coerce')

        # Assign scores
        df = assign_score(df, '评论')
        df = assign_score(df, '口味')
        df = assign_score(df, '环境')
        df = assign_score(df, '服务')

        # Calculate total score
        df = calculate_total_score(df)

        # Get top 10 by comments
        top_10_comments = df.nlargest(10, '评论')

        # Get top by comments and lowest per capita consumption
        top_lowest_per_capita = df[df['评论'] > 0].nsmallest(8, '人均消费')

        # Get top 3 by combined environment and service score
        df['环境_服务总分'] = df['环境'] + df['服务']
        highest_env_service = df.nlargest(3, '环境_服务总分')

        # Get top 3 comments and lowest service score
        top_3_comments_lowest_service = df.nlargest(3, '评论').nsmallest(3, '服务')

        # Get top recommended
        top_recommended = df.nlargest(10, '总分数')

        return render_template('index.html', 
                            top_10_comments=top_10_comments.to_dict('records'),
                            top_lowest_per_capita=top_lowest_per_capita.to_dict('records'),
                            highest_env_service=highest_env_service.to_dict('records'),
                            top_3_comments_lowest_service=top_3_comments_lowest_service.to_dict('records'),
                            top_recommended=top_recommended.to_dict('records'))

    def assign_score(df, column):
        df[f'{column}_rank'] = df[column].rank(ascending=False, method='min')
        df[f'{column}_score'] = 0
        quantiles = [df[f'{column}_rank'].quantile(i/10) for i in range(1, 10)]
        df.loc[df[f'{column}_rank'] <= quantiles[0], f'{column}_score'] = 10
        for i in range(1, 9):
            df.loc[(df[f'{column}_rank'] > quantiles[i-1]) & (df[f'{column}_rank'] <= quantiles[i]), f'{column}_score'] = 10 - i
        df.loc[df[f'{column}_rank'] > quantiles[8], f'{column}_score'] = 1
        return df

    def calculate_total_score(df):
        weights = {'评论_score': 0.55, '口味_score': 0.15, '环境_score': 0.15, '服务_score': 0.15}
        df['总分数'] = df['评论_score'] * weights['评论_score'] \
                    + df['口味_score'] * weights['口味_score'] \
                    + df['环境_score'] * weights['环境_score'] \
                    + df['服务_score'] * weights['服务_score']
        return df

    
    # Define the form
    class FoodDataForm(FlaskForm):
        mid = IntegerField('商家ID', validators=[DataRequired()])
        mname = StringField('店名', validators=[DataRequired(), Length(max=255)])
        comments_num = IntegerField('评论数量', validators=[DataRequired()])
        per_capita_con = IntegerField('人均消费', validators=[DataRequired()])
        taste = FloatField('口味评分', validators=[DataRequired(), NumberRange(min=0, max=10)])
        environment = FloatField('环境评分', validators=[DataRequired(), NumberRange(min=0, max=10)])
        service = FloatField('服务评分', validators=[DataRequired(), NumberRange(min=0, max=10)])
        phone = StringField('电话', validators=[Length(max=255)])
        address = StringField('地址', validators=[Length(max=255)])
        details = StringField('详情', validators=[Length(max=255)])
        submit = SubmitField('提交')

    @app.route('/admin/')
    def admin():
        return render_template('admin.html')
    
    @app.route('/admin/add', methods=['GET', 'POST'])
    def add():
        form = FoodDataForm()
        if form.validate_on_submit():
            food_data = FoodData(
                mid=form.mid.data,
                mname=form.mname.data,
                comments_num=form.comments_num.data,
                per_capita_con=form.per_capita_con.data,
                taste=form.taste.data,
                environment=form.environment.data,
                service=form.service.data,
                phone=form.phone.data,
                address=form.address.data,
                details=form.details.data
            )
            db.session.add(food_data)
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('add_fooddata.html', form=form)

    @app.route('/admin/delete/<mid>')
    def delete(mid):
        food_data = FoodData.query.get(mid)
        if food_data:
            db.session.delete(food_data)
            db.session.commit()
        return redirect(url_for('index'))

    @app.route('/admin/edit/<mid>', methods=['GET', 'POST'])
    def edit(mid):
        food_data = FoodData.query.get(mid)
        if not food_data:
            return redirect(url_for('index'))
        form = FoodDataForm(obj=food_data)
        if form.validate_on_submit():
            food_data.mname = form.mname.data
            food_data.comments_num = form.comments_num.data
            food_data.per_capita_con = form.per_capita_con.data
            food_data.taste = form.taste.data
            food_data.environment = form.environment.data
            food_data.service = form.service.data
            food_data.phone = form.phone.data
            food_data.address = form.address.data
            food_data.details = form.details.data
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('edit_fooddata.html', form=form)

    @app.route('/admin/search', methods=['GET', 'POST'])
    def search():
        query = request.args.get('query')
        if query:
            results = FoodData.query.filter(FoodData.mname.like(f'%{query}%')).all()
        else:
            results = FoodData.query.all()
        return render_template('search_results.html', results=results)

    if __name__ == '__main__':
        db.create_all()
        app.run(debug=True)