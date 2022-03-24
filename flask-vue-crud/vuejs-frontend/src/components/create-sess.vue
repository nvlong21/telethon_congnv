<template>
    <div id="create-sess">
        <h1>Create Sess</h1>

        <p><router-link :to="{ name: 'AllSess' }">Return to sesss</router-link></p>

        <notification v-bind:notifications="notifications"></notification>
        <!-- <form> -->
        <form v-on:submit.prevent="addSess">

            <div class="form-group">
                <label name="sess_title">Title</label>
                <input type="text" class="form-control" v-model="sess.title" id="sess_title" required>
            </div>

            <div class="form-group">
                <label name="sess_content">Phone</label>
                <input type="text" class="form-control" v-model="sess.phone" id="sess_content" required>
            </div>
            <div class="form-group">
                <button class="btn btn-primary">Get code</button>
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
            image: '',
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

        addSess: function()
        {
            var formData = new FormData();
            formData.append('title', this.sess.title);
            formData.append('phone', this.sess.phone);
            if(this.notifications) this.notifications = [];
            this.$http.post('http://localhost:8000/add_sess', formData, {
                headers : {
                    'enctype' : 'multipart/form-data'
                }
            }).then((response) => {
                if(response.data.status==1)
                {
                    this.notifications.push({
                        type: 'success',
                        message: 'Sess created successfully'
                    });
                    this.$router.push({name: 'VerifyCode', params:{"phone": this.sess.phone}}); 
                }
                this.notifications.push({
                        type: 'error',
                        message: response.data.message
                    });
                // { name: 'user', params: { username: 'eduardo' } }
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
