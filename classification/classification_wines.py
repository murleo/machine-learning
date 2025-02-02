from collections import Counter

import pandas as pd
from keras.layers import Dense, Conv1D, Flatten
from keras.layers.embeddings import Embedding
from keras.models import Sequential
from keras.preprocessing import sequence
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split

from common.get_top_xwords import filter_to_top_x
from common.config import REMOTE_DATA_URL

df = pd.read_csv(REMOTE_DATA_URL / 'wines' / 'wine_data.csv')

counter = Counter(df['variety'].tolist())
varieties_cnt = 10
top_varieties = {i[0]: idx for idx, i in enumerate(counter.most_common(varieties_cnt))}
print(top_varieties)
df = df[df['variety'].map(lambda x: x in top_varieties)]


description_list = df['description'].tolist()
# print(description_list)
mapped_list, word_list = filter_to_top_x(description_list, 2500, 10)
varietal_list_o = [top_varieties[i] for i in df['variety'].tolist()]
varietal_list = to_categorical(varietal_list_o)

max_length = 150
mapped_list = sequence.pad_sequences(mapped_list, maxlen=max_length)
train_x, test_x, train_y, test_y = train_test_split(mapped_list, varietal_list, test_size=0.3)

embedding_vector_length = 64
model = Sequential()
model.add(Embedding(2500, embedding_vector_length, input_length=max_length))
model.add(Conv1D(25, 5))
model.add(Flatten())
model.add(Dense(100, activation='relu'))
model.add(Dense(varieties_cnt, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(train_x, train_y, epochs=4, batch_size=64)

y_score = model.predict(test_x)
y_score = [[1 if i == max(sc) else 0 for i in sc] for sc in y_score]
n_right = 0
for i in range(len(y_score)):
    if all(y_score[i][j] == test_y[i][j] for j in range(len(y_score[i]))):
        n_right += 1

print("Accuracy: %.2f%%" % (n_right / len(test_y) * 100))
