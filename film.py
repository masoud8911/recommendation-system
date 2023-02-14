from connection import DBConnection
import math

connection = DBConnection()


# connection.create_table('ganre','id serial PRIMARY KEY,name varchar(50)')

# connection.create_table('film', 'id serial PRIMARY KEY , ganre_id INTEGER , name varchar(50) , CONSTRAINT fk_tbl_ganre FOREIGN KEY(ganre_id) REFERENCES ganre(id)')

# connection.create_table('users','id serial PRIMARY KEY,name varchar(50)')

# connection.create_table('comment', 'id serial PRIMARY KEY , film_id INTEGER , user_id INTEGER ,comment varchar(50),vote INTEGER , CONSTRAINT fk_tbl_film FOREIGN KEY(film_id) REFERENCES film(id) , CONSTRAINT fk_tbl_user FOREIGN KEY(user_id) REFERENCES users(id)')


def search_ganre():
    ganre = connection.select_query('ganre', '*')
    id_list = []
    for i, j in enumerate(ganre):
        print(j)
        id_list.append(ganre[i][0])

    print(id_list)

    id_ganre = int(input('Select Id Ganre For search Film : '))

    if id_ganre in id_list:
        fields = f"""ganre.name,film.name"""
        condition = f"""ganre.id=film.ganre_id and ganre.id='{id_ganre}'"""
        response = connection.select_query('ganre,film', fields, condition)
        print(response)


def search_film():
    film_name = input('Enter Your film name : ')
    condition = f"""name='{film_name}'"""
    film = connection.select_query('film', 'id,name', condition)
    print(film[0][0])

    if film:
        condition2 = f"""comment.film_id='{film[0][0]}'"""
        # For average vote for this film
        print('vote avg Is : ', connection.select_query('comment', 'AVG(vote)', condition2))

        fields = f"""film.name,comment.comment"""
        condition3 = f"""film.id=comment.film_id and comment.film_id='{film[0][0]}'"""
        response = connection.select_query('film,comment', fields, condition3)

        print(response)


def recommendation():
    condition1 = f"""user_id='{1}'"""
    current_user = connection.select_query('comment', 'film_id,vote', condition1)
    see_film_by_current_user = [film_id[0] for film_id in current_user]
    print("Film's Id see by current user : ", see_film_by_current_user)

    condition2 = f"""user_id!='{1}'"""
    # ids : all user that comment about films except current user
    ids = connection.select_query('comment', 'user_id', condition2 + 'GROUP BY(user_id)')
    # other_user : all comment and vote by other users except current user
    other_user = connection.select_query('comment', 'film_id,vote,user_id', condition2)

    for i in ids:
        count = 0  # number of film for average
        film_see_by_second_user = []  # hold film_id that see by second user
        avg1 = 0
        avg2 = 0
        both_user_see_film_id = ()

        for o in other_user:

            if o[2] == i[0] and o[0] in see_film_by_current_user:
                avg2 += o[1]
                count += 1
                both_user_see_film_id += (o[0],)

        if count > 0:
            avg2 /= count
            count = 0

        for c in current_user:
            if c[0] in both_user_see_film_id:
                avg1 += c[1]
                count += 1

        if count > 0:
            avg1 /= count
            count = 0

        f = 0  # f : numerator
        w1 = 0  # w1,2 : denominator
        w2 = 0

        if avg1 != 0 and avg2 != 0:
            condition3 = f"""user_id='{i[0]}'"""
            second_user = connection.select_query('comment', 'film_id,vote', condition3)

            for j in current_user:

                for u in second_user:

                    if j[0] == u[0]:
                        f += (j[1] - avg1) * (u[1] - avg2)
                        w1 += (j[1] - avg1) ** 2
                        w2 += (u[1] - avg2) ** 2

            w1 = math.sqrt(w1)
            w2 = math.sqrt(w2)
            w1 = w1 * w2

            if f > 0:
                f = f / w1

            print(f'similarity between current user and user with id {i[0]} : ', f)
            txt = str(both_user_see_film_id)

            if f > 0:  # condition for similarity

                condition = f"""comment.user_id='{i[0]}' and film.id not in {txt} group by(film.id)"""
                result = connection.select_query('film,comment', 'film.name', condition)
                print('recommendation film for you : ')
                print(result)


recommendation()
