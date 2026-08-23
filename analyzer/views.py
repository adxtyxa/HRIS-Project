from django.shortcuts import render
from django.core.files.storage import FileSystemStorage

from main import analyze_file


def upload_csv(request):
    context = {}

    if request.method == "POST":
        uploaded_file = request.FILES.get("csv_file")

        if not uploaded_file:
            context["error"] = "Please select a CSV file."

        elif not uploaded_file.name.lower().endswith(".csv"):
            context["error"] = "Only CSV files are allowed."

        else:
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)

            file_path = fs.path(filename)

            try:
                results = analyze_file(file_path)

                context["results"] = results

            except Exception as e:
                context["error"] = str(e)

            finally:
                fs.delete(filename)

    return render(request, "analyzer/upload.html", context)