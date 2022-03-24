<template>
    <div id="update-sess">
        <h1>Update Sess</h1>

        <p><router-link :to="{ name: 'AllSess' }">Return to sesss</router-link></p>

        <notification v-bind:notifications="notifications"></notification>

        <form v-on:submit.prevent="editSess">
            <div class="form-group">
                <label name="sess_title">Title</label>
                <input type="text" class="form-control" v-model="sess.title" id="sess_title">
            </div>

            <div class="form-group">
                <label name="sess.content">Content</label>
                <input type="text" class="form-control" v-model="sess.content" id="sess.content" required>
            </div>

            <div class="form-group">
                <label name="sess_thumbnail">Thumbnail</label>
                <div v-if="!image">
                Select an image
                        <input type="file" class="form-control" @change="onFileChange">
                </div>
                <div v-else>
                    <img :src="image" />
                    <button @click="removeImage">Remove image</button>
                </div>
            </div>

            <div class="form-group">
                <button class="btn btn-primary">Update</button>
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
                image: ''
            }
        },
        created: function(){
            this.getSess();
        },
        methods: {
            onFileChange(e) {
            var files = e.target.files || e.dataTransfer.files;
            if (!files.length)
                return;
            this.sess.file = files[0]; 
            this.createImage(files[0]);
            },
            createImage(file) {
                var image = new Image();
                var reader = new FileReader();
                var vm = this;

                reader.onload = (e) => {
                    vm.image = e.target.result;
            };
                reader.readAsDataURL(file);
            },
                removeImage: function (e) {
                this.image = '';
            },
            getSess: function()
            {
                this.$http.get('http://localhost:5000/sess/' + this.$route.params.id).then((response) => {
                    this.sess = response.body;
                    this.image = this.sess.thumbnail;
                }, (response) => {
                });
            },
            editSess: function()
            {
                var formData = new FormData();
                formData.append('title', this.sess.title);
                formData.append('content', this.sess.content);
                formData.append('file', this.sess.file);
                if(this.notifications) this.notifications = [];
                if(this.image) this.$http.put('http://localhost:5000/sess/' + this.$route.params.id, formData, {
                    headers : {
                        // 'Content-Type' : 'multipart/form-data'
                        'enctype' : 'multipart/form-data'
                    }
                }).then((response) => {
                    this.notifications.push({
                        type: 'success',
                        message: 'Sess updated successfully'
                    });
                }, (response) => {
                    this.notifications.push({
                        type: 'error',
                        message: 'Sess not updated'
                    });
                });
            }
        },
        components: {
            'notification' : Notification
        }
    }
</script>

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