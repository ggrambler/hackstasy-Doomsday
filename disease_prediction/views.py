from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
import numpy as np
import joblib,json
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from concurrent.futures import ThreadPoolExecutor
import os

# ------------------------------
# DATA LOADING FUNCTIONS
# ------------------------------

def load_symptoms_data():
    """Load symptom severity data with caching."""
    cache_file = 'dataset/symptoms_cache.pkl'
    if os.path.exists(cache_file):
        return joblib.load(cache_file)
    else:
        try:
            df_symptoms = pd.read_csv('dataset/Symptom-severity.csv')
            joblib.dump(df_symptoms, cache_file)
            return df_symptoms
        except FileNotFoundError:
            raise FileNotFoundError("Symptom-severity.csv not found in the dataset folder.")


def load_model():
    """Load the trained ensemble model or train it if not available."""
    model_file = "dataset/ensemble_model_parallel.joblib"
    if os.path.exists(model_file):
        return joblib.load(model_file)
    else:
        return train_and_save_model()


# ------------------------------
# DATA PREPROCESSING
# ------------------------------

def clean_and_encode_data(df):
    """Clean and encode symptom data."""
    df.fillna(0, inplace=True)
    df = df.applymap(lambda x: x.lower().strip() if isinstance(x, str) else x)
    df.replace(['dischromic _patches', 'spotting_ urination', 'foul_smell_of urine'], 0, inplace=True)
    
    df_symptoms = load_symptoms_data()
    symptom_dict = dict(zip(df_symptoms['Symptom'].str.lower().str.strip(), df_symptoms['weight']))
    
    for symptom, weight in symptom_dict.items():
        df.replace(symptom, weight, inplace=True)
    
    return df


# ------------------------------
# MODEL TRAINING
# ------------------------------

def train_and_save_model():
    """Train models in parallel and create an ensemble model."""
    try:
        df = pd.read_csv('dataset/dataset.csv')
        df = clean_and_encode_data(df)

        data = df.iloc[:, 1:].values
        labels = df['Disease'].values

        x_train, x_test, y_train, y_test = train_test_split(data, labels, train_size=0.85, shuffle=True, random_state=42)

        models = {
            'svm': (SVC(probability=True), {'C': [0.1, 1, 10], 'gamma': ['scale', 'auto']}),
            'rf': (RandomForestClassifier(random_state=42), {'n_estimators': [50, 100, 150]}),
            'gb': (GradientBoostingClassifier(random_state=42), {'n_estimators': [50, 100, 150]})
        }

        trained_models = {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(train_model, name, model, x_train, y_train, params)
                for name, (model, params) in models.items()
            }
            for future in futures:
                model_name, best_model = future.result()
                trained_models[model_name] = best_model

        # Ensemble Voting Classifier
        ensemble_model = VotingClassifier(
            estimators=[(name, trained_models[name]) for name in trained_models],
            voting='soft'
        )
        ensemble_model.fit(x_train, y_train)
        joblib.dump(ensemble_model, "dataset/ensemble_model_parallel.joblib")
        return ensemble_model

    except FileNotFoundError:
        raise FileNotFoundError("Dataset.csv not found in the dataset folder.")
    except Exception as e:
        raise Exception(f"Error during model training: {str(e)}")


def train_model(model_name, model, x_train, y_train, param_grid):
    """Train an individual model with GridSearchCV."""
    print(f"Training {model_name}...")
    grid_search = GridSearchCV(model, param_grid, cv=5, n_jobs=-1, verbose=1)
    grid_search.fit(x_train, y_train)
    print(f"{model_name} training complete.")
    return model_name, grid_search.best_estimator_


# ------------------------------
# PREDICTION FUNCTION
# ------------------------------

def get_symptom_weight(symptom, df_symptoms):
    """Get weight of a specific symptom."""
    symptom_dict = dict(zip(df_symptoms['Symptom'].str.lower().str.strip(), df_symptoms['weight']))
    return symptom_dict.get(symptom.lower().strip(), 0)


def disease_info(request):
    """Fetch disease description and precautions."""
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        predicted_disease = data.get('disease')
        if not predicted_disease:
            return JsonResponse({'status': 'error', 'message': 'No disease provided'}, status=400)

        try:
            disease_description_df = pd.read_csv('dataset/disease_Description.csv')
            disease_precaution_df = pd.read_csv('dataset/disease_precaution.csv')

            description_row = disease_description_df.loc[
                disease_description_df['Disease'].str.lower().str.strip() == predicted_disease.lower().strip()
            ]
            precautions_row = disease_precaution_df.loc[
                disease_precaution_df['Disease'].str.lower().str.strip() == predicted_disease.lower().strip()
            ]

            description = description_row['Description'].iloc[0] if not description_row.empty else 'No description available.'
            precautions = precautions_row.iloc[0][1:].dropna().tolist() if not precautions_row.empty else ['No precautions available.']
            
            return JsonResponse({'status': 'success', 'description': description, 'precautions': precautions})

        except FileNotFoundError:
            return JsonResponse({'status': 'error', 'message': 'Disease data files not found.'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def predict_disease(request):
    """Handle disease prediction requests."""
    if request.method == 'POST':
        symptoms = request.POST.getlist('symptoms')
        if not symptoms:
            return JsonResponse({'status': 'error', 'message': 'No symptoms provided'}, status=400)

        try:
            df_symptoms = load_symptoms_data()
            model = load_model()
            symptom_weights = np.array([get_symptom_weight(symptom, df_symptoms) for symptom in symptoms])
            encoded_symptoms = np.concatenate((symptom_weights, np.zeros(17 - len(symptom_weights))))
            prediction = model.predict([encoded_symptoms])
            return JsonResponse({'status': 'success', 'prediction': prediction[0]})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # GET Request: Render prediction template
    df_symptoms = load_symptoms_data()
    symptoms_list = df_symptoms['Symptom'].tolist()
    indices = list(range(5))
    return render(request, 'disease_prediction/predict_disease.html', {'symptoms': symptoms_list, 'indices': indices})
