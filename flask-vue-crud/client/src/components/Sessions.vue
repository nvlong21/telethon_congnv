<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Sesss</h1>
        <hr><br><br>
        <alert :message=message v-if="showMessage"></alert>
        <button type="button" class="btn btn-success btn-sm" v-b-modal.sess-modal>Add Sess</button>
        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Title</th>
              <th scope="col">Phone</th>
              <th scope="col">Read?</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(sess, index) in sesss" :key="index">
              <td>{{ sess.title }}</td>
              <td>{{ sess.phone }}</td>
              <td>
                <span v-if="sess.status">Yes</span>
                <span v-else>No</span>
              </td>
              <td>
                <div class="btn-group" role="group">
                  <button
                          type="button"
                          class="btn btn-warning btn-sm"
                          v-b-modal.sess-update-modal
                          @click="editSess(sess)">
                      Update
                  </button>
                  <button
                          type="button"
                          class="btn btn-danger btn-sm"
                          @click="onDeleteSess(sess)">
                      Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <b-modal ref="addSessModal"
            id="sess-modal"
            title="Add a new sess"
            hide-footer>
      <b-form @submit="onSubmit" @reset="onReset" class="w-100">
      <b-form-group id="form-title-group"
                    label="Title:"
                    label-for="form-title-input">
          <b-form-input id="form-title-input"
                        type="text"
                        v-model="addSessForm.title"
                        required
                        placeholder="Enter title">
          </b-form-input>
        </b-form-group>
        <b-form-group id="form-phone-group"
                      label="Phone:"
                      label-for="form-phone-input">
            <b-form-input id="form-phone-input"
                          type="text"
                          v-model="addSessForm.phone"
                          required
                          placeholder="Enter phone">
            </b-form-input>
          </b-form-group>
        <b-button-group>
          <b-button type="submit" variant="primary">Submit</b-button>
          <b-button type="reset" variant="danger">Reset</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
        <b-modal ref="addSessCodeModal"
            id="sess-code-modal"
            title="Add a new sess"
            hide-footer>
      <b-form @submit="onSubmitCode" @reset="onResetCode" class="w-100">
      <b-form-group id="form-code-group"
                    label="Code:"
                    label-for="form-code-input">
        </b-form-group>
        <b-form-group id="form-code-group"
                      label="Phone:"
                      label-for="form-code-input">
            <b-form-input id="form-code-input"
                          type="text"
                          v-model="addSessCodeForm.code"
                          required
                          placeholder="Enter code">
            </b-form-input>
          </b-form-group>
        <b-button-group>
          <b-button type="submit" variant="primary">Submit</b-button>
          <b-button type="reset" variant="danger">Reset</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
    <b-modal ref="editSessModal"
            id="sess-update-modal"
            title="Update"
            hide-footer>
      <b-form @submit="onSubmitUpdate" @reset="onResetUpdate" class="w-100">
      <b-form-group id="form-title-edit-group"
                    label="Title:"
                    label-for="form-title-edit-input">
          <b-form-input id="form-title-edit-input"
                        type="text"
                        v-model="editForm.title"
                        required
                        placeholder="Enter title">
          </b-form-input>
        </b-form-group>
        <b-form-group id="form-phone-edit-group"
                      label="Phone:"
                      label-for="form-phone-edit-input">
            <b-form-input id="form-phone-edit-input"
                          type="text"
                          v-model="editForm.phone"
                          required
                          placeholder="Enter phone">
            </b-form-input>
          </b-form-group>
        <b-form-group id="form-status-edit-group">
          <b-form-checkbox-group v-model="editForm.status" id="form-checks">
            <b-form-checkbox value="true">Read?</b-form-checkbox>
          </b-form-checkbox-group>
        </b-form-group>
        <b-button-group>
          <b-button type="submit" variant="primary">Update</b-button>
          <b-button type="reset" variant="danger">Cancel</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import axios from 'axios';
import Alert from './Alert.vue';

export default {
  data() {
    return {
      sesss: [],
      addSessForm: {
        title: '',
        phone: '',
        status: [],
      },
      addSessCodeForm: {
        code: '',
      },
      message: '',
      showMessage: false,
      editForm: {
        id: '',
        title: '',
        phone: '',
        status: [],
      },
    };
  },
  components: {
    alert: Alert,
  },
  methods: {
    getSesss() {
      const path = 'http://localhost:5000/sesss';
      axios.get(path)
        .then((res) => {
          this.sesss = res.data.sesss;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addSess(payload) {
      const path = 'http://localhost:5000/sesss';
      axios.post(path, payload)
        .then(() => {
          this.getSesss();
          this.message = 'Sess added!';
          this.showMessage = true;
          this.$refs.addSessCodeModal.modal('show');
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
          this.getSesss();
        });
    },
    initForm() {
      this.addSessForm.title = '';
      this.addSessForm.phone = '';
      this.addSessForm.status = [];
      this.editForm.id = '';
      this.editForm.title = '';
      this.editForm.phone = '';
      this.editForm.status = [];
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addSessModal.hide();
      let status = false;
      if (this.addSessForm.status[0]) status = true;
      const payload = {
        title: this.addSessForm.title,
        phone: this.addSessForm.phone,
        status, // property shorthand
      };
      this.addSess(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addSessModal.hide();
      this.initForm();
    },
    editSess(sess) {
      this.editForm = sess;
    },
    onSubmitUpdate(evt) {
      evt.preventDefault();
      this.$refs.editSessModal.hide();
      let status = false;
      if (this.editForm.status[0]) status = true;
      const payload = {
        title: this.editForm.title,
        phone: this.editForm.phone,
        status,
      };
      this.updateSess(payload, this.editForm.id);
    },
    updateSess(payload, sessID) {
      const path = `http://localhost:5000/sesss/${sessID}`;
      axios.put(path, payload)
        .then(() => {
          this.getSesss();
          this.message = 'Sess updated!';
          this.showMessage = true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.getSesss();
        });
    },
    onResetUpdate(evt) {
      evt.preventDefault();
      this.$refs.editSessModal.hide();
      this.initForm();
      this.getSesss(); // why?
    },
    removeSess(sessID) {
      const path = `http://localhost:5000/sesss/${sessID}`;
      axios.delete(path)
        .then(() => {
          this.getSesss();
          this.message = 'Sess removed!';
          this.showMessage = true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.getSesss();
        });
    },
    onDeleteSess(sess) {
      this.removeSess(sess.id);
    },
  },
  created() {
    this.getSesss();
  },
};
</script>
