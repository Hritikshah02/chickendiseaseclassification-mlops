from src.cnnClassifier.entity.config_entity import TrainingConfig
import tensorflow as tf
from pathlib import Path


class Training: 
    def __init__(self, config: TrainingConfig): 
        self.config = config
    
    def get_base_model(self): 
        self.model = tf.keras.models.load_model(
        self.config.updated_base_model_path
    )

    # 🔴 FIX: Recompile the model with a fresh optimizer
        self.model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),  
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )


    def train_valid_generator(self): 
        
        datagenerator_kawrgs = dict(
            rescale = 1./255,
            validation_split = 0.20
        )

        dataflow_kwargs = dict(
            target_size = self.config.params_image_size[:-1],
            batch_size = self.config.params_batch_size,
            interpolation = "bilinear"
        )

        valid_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
            **datagenerator_kawrgs
        )

        self.valid_generator = valid_datagen.flow_from_directory(
            directory=self.config.training_data,
            subset="validation",
            shuffle=False, 
            **dataflow_kwargs
        )

        if self.config.params_is_augmentation: 
            train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
                rotation_range=40,
                horizontal_flip=True,
                width_shift_range=0.2, 
                height_shift_range=0.2,
                shear_range=0.2,
                zoom_range=0.2,
                **datagenerator_kawrgs
            )
        else: 
            train_datagen = valid_datagen

        self.train_generator = train_datagen.flow_from_directory(
            directory=self.config.training_data,
            subset="training",
            shuffle=True,
            **dataflow_kwargs
        )
    
    @staticmethod
    def save_model(path: Path, model: tf.keras.Model): 
        model.save(path)

    def train(self, callback_list: list): 
        self.steps_per_epoch = self.train_generator.samples // self.train_generator.batch_size
        self.validation_steps = self.valid_generator.samples // self.valid_generator.batch_size

        self.history = self.model.fit(
            self.train_generator, 
            epochs=self.config.params_epochs,
            steps_per_epoch=self.steps_per_epoch,
            validation_data=self.valid_generator,
            validation_steps = self.validation_steps,
            callbacks = callback_list
        )

        self.save_model(
            path=self.config.trained_model_path,
            model = self.model
        )