from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Dropout, BatchNormalization, Flatten, Dense, Activation
from tensorflow.keras.models import Sequential
import tensorflow as tf

def train_cnn_model(X_train, y_train, X_test, y_test, input_shape=(141, 1), num_classes=8, batch_size=32, epochs=50):

    # Model Architecture
    model_cnn = Sequential([
        # Conv1D Layer 1: 64 filters, kernel_size=8, input_shape=(141, 1)
        # Input shape: (3304, 141, 1) -> Output shape: (3304, 134, 64)
        Conv1D(64, kernel_size=8, input_shape=input_shape),
        BatchNormalization(),
        Activation('relu'),


        # Conv1D Layer 2: 128 filters, kernel_size=8
        # Input shape: (3304, 134, 64) -> Output shape: (3304, 127, 128)
        Conv1D(128, kernel_size=8),
        BatchNormalization(),
        Activation('relu'),
        # MaxPooling1D Layer: Pool size=4
        # Input shape: (3304, 127, 128) -> Output shape: (3304, 31, 128)
        MaxPooling1D(pool_size=4),
        Dropout(0.2),


        # Conv1D Layer 3: 128 filters, kernel_size=8
        # Input shape: (3304, 31, 128) -> Output shape: (3304, 24, 128)
        Conv1D(128, kernel_size=8),
        BatchNormalization(),
        Activation('relu'),
        # MaxPooling1D Layer: Pool size=4
        # Input shape: (3304, 24, 128) -> Output shape: (3304, 6, 128)
        MaxPooling1D(pool_size=4),
        Dropout(0.2),


        # Flatten Layer: Flatten the input
        # Input shape: (3304, 6, 128) -> Output shape: (3304, 768)
        Flatten(),
        # Dense Layer: 256 units
        # Input shape: (3304, 768) -> Output shape: (3304, 256)
        Dense(256, activation='relu'),
        Dropout(0.3),
        # Dense Layer: Output layer with 8 classes
        # Input shape: (3304, 256) -> Output shape: (3304, 8)
        Dense(num_classes, activation='softmax')
    ])

    # Early stopping callback
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    # Compile the Model
    model_cnn.compile(
        loss='categorical_crossentropy',
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        metrics=['accuracy']
    )

    # Train the Model
    history = model_cnn.fit(
        X_train, y_train,
        batch_size=batch_size,
        epochs=epochs,
        validation_data=(X_test, y_test),
        callbacks=[early_stopping]
    )

    return history, model_cnn