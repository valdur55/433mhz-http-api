
<!doctype html>
<script src="https://code.jquery.com/jquery-3.6.1.slim.min.js"></script>
<link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
<form id="sendCmd">
    <label>
        <select class="js-example-basic-single" name="cmd" id="cmd">
            % for item in shortcuts:
            <option value="{{item}}">{{item}}</option>
            % end
        </select>
    </label>
    <button type="submit">Send</button>
    <div id="result"></div>
</form>
<script>
    $(document).ready(function() {
        $('#cmd').select2();
    });
    // this is the id of the form
    $("#sendCmd").submit(function(e) {

        e.preventDefault(); // avoid to execute the actual submit of the form.

        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                document.getElementById("result").innerHTML = xhttp.responseText;
            }
        };
        xhttp.open("GET", "/?cmd="+$("#cmd").val(), true);
        xhttp.send();
    });
</script>
