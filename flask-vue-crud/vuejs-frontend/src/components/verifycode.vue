<template>
    <div id="create-sess">
        <h1>Create Sess</h1>

        <notification v-bind:notifications="notifications"></notification>
        <!-- <form> -->
        <form v-on:submit.prevent="addCode">

            <div class="form-group">
                <label name="code_content">Code</label>
                <input type="text" class="form-control" v-model="sess.code" id="code_content" required>
            </div>
            <div class="form-group">
                <button class="btn btn-primary">Verify</button>
            </div>
        </form>
    </div>
</template>

<script>

import Notification from './notifications.vue';
export default{
    
    data(){
        return{
            sess:{},
            notifications:[],
            phone: this.$route.params.phone,
        }
    },
    methods: {
        
        // onFileChange(e) {
        //     var files = e.target.files || e.dataTransfer.files;
        //     if (!files.length)
        //         return;
        //     this.sess.file = files[0];
        //     this.createImage(files[0]);
        //     },
        //     createImage(file) {
        //     var image = new Image();
        //     var reader = new FileReader();
        //     var vm = this;

        //     reader.onload = (e) => {
        //         vm.image = e.target.result;
        //     };
        //     reader.readAsDataURL(file);
        //     },
        //     removeImage: function (e) {
        //     this.image = '';
        //     },

        addCode: function()
        {
            
            var formData = new FormData();
            formData.append('code', this.sess.code);
            formData.append('phone', this.phone);
            this.$http.post('http://localhost:8000/verify-code', formData, {
                headers : {
                    'enctype' : 'multipart/form-data'
                }
            }).then((response) => {
               
                this.notifications.push({
                    type: 'success',
                    message: 'Sess created successfully'
                });
                this.$router.push('/') 
            }, (response) => {
                this.notifications.push({
                    type: 'error',
                    message: 'Sess not created'
                });
            });
        }
    },
    components: {
        'notification' : Notification
    }
}

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
img {
  width: 30%;
  margin: auto;
  display: block;
  margin-bottom: 10px;
}
button {
  
}
</style>
